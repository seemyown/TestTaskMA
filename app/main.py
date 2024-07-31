from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str, req: Request):
    req.stream()
    return {"message": f"Hello {name}"}
