from fastapi import APIRouter

router = APIRouter()

@router.get("/{conversation_id}/messages")
def get_conversation_messages(conversation_id: int):
    return {"conversation_id": conversation_id, "messages": []}
