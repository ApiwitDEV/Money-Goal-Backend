from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test")
async def test():
    return "test"

# if __name__ == "__main__":
#     config = uvicorn.Config("main:app", port=8000, log_level="info")
#     server = uvicorn.Server(config)
#     server.run()