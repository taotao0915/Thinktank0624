import uvicorn
from fastapi import FastAPI
from starlette.responses import JSONResponse, FileResponse, Response, RedirectResponse, HTMLResponse, PlainTextResponse

app = FastAPI(
    title="atguigu",
    version="1.0",
    description="测试用的接口"
)

@app.get("/api/user")
async def get_user():
    return JSONResponse(
        status_code=200,
        content={
            "name":"nick",
            "age":22,
        }
    )

#后端返回的响应头是给浏览器看的，浏览器看到响应头里面的信息就会根据这些信息做不同的处理
@app.get("/download")
async def download():
    return FileResponse(
        path=r"C:\Users\94702\Desktop\test.png",
        media_type="image/jpeg",
        headers={
            # 告诉浏览器这是一个附件，并且文件名是啥 浏览器看到这个头信息就会自动下载，而不是默认显示
            "Content-Disposition": "attachment; filename=mylove08.jpg"
        }
    )



# todo 03 返回纯文本  几乎不用  只有当你需要返回一些日志的时候
@app.get("/text")
async def get_text():
    return PlainTextResponse(content="<h2>这是纯文本响应</h2>", status_code=200)

# todo 04 返回html内容  几乎不用 前后端分离了以后这个写法就几乎不用了
@app.get("/hello")
async def hello(name: str = "游客"):
    return HTMLResponse(content="<h2>这是hello响应</h2>", status_code=200)

# todo 05 返回重定向  目前几乎不用
@app.get("/old-path")
async def redirect_old_path():
    # 重定向到 /new-path，状态码 307 表示临时重定向
    return RedirectResponse(url="/new-path", status_code=307)

@app.get("/new-path")
async def new_path():
    return {"message": "这是新接口"}



# todo 06 返回自己指定的响应类型  目前几乎不用
@app.get("/custom")
async def custom_response():
    # 返回二进制数据，指定自定义 MIME 类型
    return Response(
        content="<h1>纯文本</h1>",
        media_type="text/plain",
        # media_type="text/html",
        status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)