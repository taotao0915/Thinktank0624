import json
import uuid

from fastapi import FastAPI, Path, Body, BackgroundTasks
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from atguigu.query_process.main_graph import QueryMainGraphRunner
from atguigu.tool.mongo_tool import get_recent_messages, clear_history
from atguigu.tool.task_utils import update_task_status, TASK_STATUS_PROCESSING, create_queue, put_data, get_task_info, \
    TASK_STATUS_COMPLETED, TASK_STATUS_FAILED, get_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]  # 允许跨域请求的头信息
)

# 1、健康检查接口 主要就是看看页面和后台能不能连接
@app.get("/health")
def health():
    return {"hehe": "yangmi"}


# 2、获取历史会话记录，返回{"items":[]}
@app.get("/history/{session_id}")
def history(session_id: str = Path(...,description="会话id")):
    history_list = get_recent_messages(session_id)
    history_list = [{
        **item,
        "_id": str(item.get("_id")),
    } for item in history_list]
    history_list.sort(key=lambda item: item["ts"])

    return {"items": history_list}

# 3、删除历史会话记录
@app.delete("/history/{session_id}")
def delete_history(session_id: str = Path(...,description="会话id")):
    clear_history(session_id)
    return {"message": "ok"}


class BodyParams(BaseModel):
    session_id:str = Field(...,description="会话id")
    query:str = Field(...,description="用户问题")



def run_main_graph(task_id,session_id,query):
    init_state = {
        "session_id": session_id,
        "original_query": query,
        "task_id": task_id
    }

    #全局状态实时数据修改的位置
    try:
        # 更新任务状态
        #前面我们使用轮询的时候，只管更新就完事，因为专门有接口在返回这些修改的状态数据列表
        #这次我们使用sse,sse是我们要主动推送队列当中的数据给前端，因此我们要手动把更新的状态数据存入队列
        update_task_status(task_id,TASK_STATUS_PROCESSING)
        put_data(task_id,"progress",get_task_info(task_id))

        QueryMainGraphRunner.create_and_run(init_state)

        update_task_status(task_id, TASK_STATUS_COMPLETED)
        put_data(task_id, "progress", get_task_info(task_id))

    except:
        update_task_status(task_id, TASK_STATUS_FAILED)
        put_data(task_id, "error", get_task_info(task_id))
        raise

@app.post("/query")
def query(background_tasks:BackgroundTasks, body_params: BodyParams = Body(...,description="请求体参数")):
    task_id = str(uuid.uuid4())
    session_id = body_params.session_id
    query = body_params.query

    #启动后台任务执行graph流程
    #在这里准备队列
    create_queue(task_id)
    background_tasks.add_task(run_main_graph,task_id,session_id,query)


    return {
        "task_id":task_id
    }




#sse使用流式响应推送实时状态数据
@app.get("/stream/{task_id}")
def stream(task_id: str = Path(...,description="任务id")):

    def generate_data():
        while True:
            item = get_data(task_id)
            yield f"event: {item.get('event')}\n"
            #不能使用工具json_format 因为工具的缩进是4个空格，不符合sse的要求
            yield f"data: {json.dumps(item.get('data'),ensure_ascii=False)}\n\n"

    return StreamingResponse(generate_data(), media_type="text/event-stream")



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)