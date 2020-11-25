import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

some_file_path = "media/books/a/0_1.png"
app = FastAPI()



@app.get("/")
async def main():
    file_like = open(some_file_path, mode="rb")
    return StreamingResponse(file_like)

if __name__ == "__main__":
    uvicorn.run("fastapi_file:app", host="0.0.0.0", port=8888, reload=True)