from fastapi import FastAPI

app = FastAPI(title="Todo App", version="0.1.0")


@app.get("/")
async def read_root() -> dict[str, str]:
    """Return a welcome message for the API."""
    return {"message": "Welcome to the Todo API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Return the API health status."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
