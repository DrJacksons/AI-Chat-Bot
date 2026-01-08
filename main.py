import uvicorn
from server.setting import config


if __name__ == "__main__":
    reload = True if config.ENVIRONMENT != "production" else False
    uvicorn.run(
        "server.core.server:app",
        host="127.0.0.1",
        port=8000,
        workers=1,
        reload=reload,
    )
