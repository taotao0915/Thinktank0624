import time

from fastapi import FastAPI, BackgroundTasks

app = FastAPI(
    title="atguigu",
    version="1.0",
    description="测试用的接口"
)


@app.get("/")
def index():
    return {"message": "Hello World"}



def task(n):
    while n > 0:
        print(f"我爱你杨幂{n}")
        time.sleep(1)
        n -= 1


@app.get("/testbackgroundtask")
async def testbackgroundtask(backgroundtasks: BackgroundTasks):
    #backgroundtasks后台任务是异步效果，所以不会阻塞代码的执行
    #接口在调用的时候会立即返回，但是后台任务会继续执行
    #后期我们项目当中的graph，就是在后台任务当中去执行的
    #后台任务本身就是异步效果，所以后台任务当中的代码，最好写同步，如果写成异步
    # 那么后台任务当中只要是有异步都得写成异步，这样就会造成嵌套的异步，代码就会很麻烦
    # 此时遇到这样的情况，其实就不应该选择后台任务这个技术做这样的事
    backgroundtasks.add_task(task,100)
    return {"msg":"ok"}








if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0", #谁可以访问
        port=8000,
    )

