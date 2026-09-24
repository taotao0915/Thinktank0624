import time
from queue import Queue

from fastapi import FastAPI, BackgroundTasks, Query
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

app = FastAPI(
    title="atguigu",
    version="1.0",
    description="测试用的接口"
)

#解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



queue_dict = {}

def make_email(session_id: str):
    if session_id not in queue_dict:
        queue_dict[session_id] = Queue()
    q = queue_dict.get(session_id)

    #给队列当中添加邮件数据
    q.put("我爱杨幂1")
    q.put("我爱杨幂2")
    q.put("我爱杨幂3")
    q.put("我爱杨幂4")
    q.put("我爱杨幂5")
    q.put(None)



@app.get("/send_email")
async def send_email(
    background_tasks: BackgroundTasks,
    session_id: str=Query(...,description="session_id")
):
    background_tasks.add_task(make_email,session_id=session_id)
    return {"message": "开始制造邮件准备发送"}


@app.get("/sse01")
async def sse01(
        session_id: str=Query(...,description="session_id")
):
    # todo 第四步
    def generate_email():
    #     获取对应的队列，通过yield一个一个返回队列当中的邮件数据
        while queue_dict.get(session_id) is None:
            # 等待队列创建完成
            time.sleep(1)
        q = queue_dict.get(session_id)
        while True:
            time.sleep(1)
            data = q.get()
            yield f"data: {data}\n\n"#sse推送数据的语法，不能随便修改
            if data is None:
                break
    return StreamingResponse(generate_email(),media_type="text/event-stream")




if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0", #谁可以访问
        port=8000,
    )
