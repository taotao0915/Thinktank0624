import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Demo",
    version="0.1.0",
    description="FastAPI Demo",
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8000)