from fastapi import FastAPI

from app.api.seed import router as seed_router
from app.api.predict import router as predict_router

app = FastAPI()
app.include_router(seed_router)
app.include_router(predict_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
