# 1. 创建应用
import shutil
import time
import uuid
from pathlib import Path

import fastapi
import uvicorn
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime

from atguigu.config.config import MinioConfig
from atguigu.tool.json_format_tool import json_format
from atguigu.tool.logger import logger
from atguigu.tool.minio_client_tool import get_minio_client
from atguigu.tool.task_utils import get_task_info, update_task_status, TASK_STATUS_PROCESSING, TASK_STATUS_COMPLETED, \
    TASK_STATUS_FAILED, add_running_task, add_done_task, add_node_duration
from import_process.main_graph import MainGraph

app = FastAPI(
    title="掌柜智库-导入API",
    description="此文档是掌柜智库导入流程的API接口说明"
)

# 2. 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)

# 后台任务用来执行main_graph
def run_main_graph(task_id,local_dir,local_file_path):
    init_state = {
        "task_id":task_id,
        "local_dir":local_dir,
        "local_file_path":local_file_path,
    }
    # 这里就是专门修改全局状态的位置

    try:
        update_task_status(task_id,TASK_STATUS_PROCESSING) #设置全局状态为处理中
        result = MainGraph.create_and_run(init_state)
        logger.info(json_format(result))
        update_task_status(task_id, TASK_STATUS_COMPLETED) # 设置全局状态为完成
    except:
        update_task_status(task_id, TASK_STATUS_FAILED) # 设置全局状态为失败
        raise



@app.post("/upload")
def upload_file(background_task:BackgroundTasks,file: UploadFile = File(...,description="上传文件")):
    task_id = str(uuid.uuid4())

    # 把文件暂存到本地
    add_running_task(task_id,"upload_file")
    start_time = time.time()

    local_dir = rf"D:\output\{datetime.now().strftime('%Y%m%d')}"
    local_dir_obj = Path(local_dir)
    local_file_path = str(local_dir_obj / file.filename)
    local_dir_obj.mkdir(parents=True, exist_ok=True)
    with open(local_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f, 1024*1024)

    # 把本地的这个文件转储到minio
    minio_client = get_minio_client()
    minio_client.fput_object(
        bucket_name=MinioConfig.minio_bucket_name,
        object_name=f"pdf_file/{datetime.now().strftime('%Y%m%d')}/{file.filename}",
        file_path=local_file_path
    )
    end_time = time.time()

    add_done_task(task_id, "upload_file")
    add_node_duration(task_id,"upload_file",end_time - start_time)

    # 上传文件完成就启动后台任务专门运行graph
    background_task.add_task(run_main_graph,task_id,local_dir,local_file_path)



    return {
        "task_id": task_id,
    }


@app.get("/status/{task_id}")
def get_status(task_id: str = fastapi.Path(...,description="任务ID")):
    return get_task_info(task_id)






# 7. 启动项目
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)