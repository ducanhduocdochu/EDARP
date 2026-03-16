import uvicorn

from .config import HOST, PORT

if __name__ == "__main__":
    uvicorn.run("embedding_service.app:app", host=HOST, port=PORT, reload=True)
