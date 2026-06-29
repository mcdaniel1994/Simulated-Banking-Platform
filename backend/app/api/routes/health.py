from fastapi import APIRouter

router = APIRouter()


# Report process liveness without depending on the database or other external services.
@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
