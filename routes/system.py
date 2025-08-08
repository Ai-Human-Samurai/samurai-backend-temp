from fastapi import APIRouter

router = APIRouter()

APP_VERSION = "1.0.0"
SUPPORTED_LANGUAGES = ["ru", "en", "ja"] 

@router.get("/status", tags=["system"])
def status():
    return {
        "status": "ok",
        "version": APP_VERSION,
        "languages": SUPPORTED_LANGUAGES,
        "message": "Samurai API is running."
    }