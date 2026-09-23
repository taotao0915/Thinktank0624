import shutil
import uuid

import uvicorn
from fastapi import FastAPI, Body, Query, Path, Depends, UploadFile
from pydantic import BaseModel, Field
from starlette.requests import Request

app = FastAPI(
    title="FastAPI Demo",
    version="0.1.0",
    description="FastAPI Demo",
)


@app.get("/testpath/{id}/{name}")
async def testpath(
        id: int = Path(...,gt=1,le=100),
        name: str = Path(...,description="姓名")
):
    return {"id": id, "name": name}




@app.get("/testquery")
async def testquery(
        id:int,
        name:str=Query(...,description="用户名"),
        age:int=0
):
    return {"id": id, "name": name, "age": age}


class User(BaseModel):
    name:str=Field(...,description="用户名"),
    age:int=Field(default=18,description="用户年龄")

@app.post("/testbody")
async def testbody(
        user:User=Body(...,description="用户信息")
):
    print(type(user))
    return user



@app.post("/testmix/{id}")
async def testmix(
        id:int=Path(...,description="用户id"),
        username:str=Query(...,description="用户名"),
        user:User=Body(...,description="用户体")
):
    return {"id": id, "username": username, "user": user}



class Params:
    def __init__(self,id,name,password):
        self.id = id
        self.name = name
        self.password = password

@app.post("/testmix2/{id}")
async def testmix2(
    params:Params=Depends(Params),
    user:User=Body(...,description="用户体")
):
    return {"id": params.id, "name":params.name,"password":params.password, "user": user}



@app.get("/testheader")
def testheader(request:Request):
    token = request.headers.get("token")
    return {"token":token}



@app.post("/upload")
def upload_file(file:UploadFile):
    uuid_str = str(uuid.uuid4())
    file_name = uuid_str[:9] + file.filename
    with open(file_name, "wb") as f:
        shutil.copyfileobj(file.file, f, 1024*1024)

    return {"msg":"ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)