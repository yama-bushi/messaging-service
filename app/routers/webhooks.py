from fastapi import APIRouter

router = APIRouter()

@router.post("/sms")
def sms_webhook():
    return {"detail": "sms webhook placeholder"}

@router.post("/email")
def email_webhook():
    return {"detail": "email webhook placeholder"}
