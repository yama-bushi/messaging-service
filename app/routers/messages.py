from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def send_message():
    return {"detail": "send endpoint placeholder"}
