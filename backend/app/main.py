from fastapi import FastAPI
from app.api.validate import router as validate_router
from app.api.extract import router as extract_router
from app.api.extract_delta import router as delta_router


app = FastAPI(
    title="LLM Context Bridge",
    version="0.1.0"
)

app.include_router(validate_router)
app.include_router(extract_router)
app.include_router(delta_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
