# 目标：后端先接收查询请求，后台处理，SSE 推送处理结果
#
# 案例2 使用post请求加异步操作
# 	1、前端发请求传递一个query，再传递一个session_id  两个参数到后端进行请求体接收
# 	2、后端写一个接口获取这两个参数，并返回给前端收到的消息，并启动task造消息
# 	3、前端订阅sse请求
# 	4、服务端需要写sse回复接口，从task当中获取自己的队列，从队列当中一个一个yield答案
import asyncio
import time
from fastapi import FastAPI, Query, BackgroundTasks, Body
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from asyncio import Queue

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

class BodyParams(BaseModel):
    query:str = Field(...,description="用户问题")
    session_id:str = Field(...,description="会话id")


queue_dict = {}

async def make_email(query,session_id):
    if session_id not in queue_dict:
        queue_dict[session_id] = Queue()
    q = queue_dict.get(session_id)

    await q.put("我爱赵丽颖1")
    await q.put("我爱赵丽颖2")
    await q.put("我爱赵丽颖3")
    await q.put("我爱赵丽颖4")
    await q.put("我爱赵丽颖5")
    await q.put(None)



@app.post("/send_email")
async def send_email(background_tasks:BackgroundTasks, body_params:BodyParams = Body(...,description="请求体参数")):
    query = body_params.query
    session_id = body_params.session_id
    # print(query,session_id)

    background_tasks.add_task(make_email,query,session_id)


    return {"message": "开始制造邮件准备发送"}


async def generate_email(session_id):
    while queue_dict.get(session_id) is None:
        await asyncio.sleep(1)
    q = queue_dict.get(session_id)

    while True:
        await asyncio.sleep(1)
        data = await q.get()
        yield f"data: {data}\n\n"
        if data is None:
            break




@app.get("/sse02")
async def sse02(session_id:str = Query(...,description="会话id")):
    return StreamingResponse(generate_email(session_id), media_type="text/event-stream")



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0", #谁可以访问
        port=8000,
    )

