import uvicorn

from .config import HOST, PORT

if __name__ == "__main__":
    uvicorn.run("indexing_service.app:app", host=HOST, port=PORT, reload=True)
