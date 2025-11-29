from typing import Optional


class ConversationService:
    """
    Handles conversation lookup/creation based on participants.

    """

    def get_or_create_conversation_id(
        self,
        db,
        from_address: str,
        to_address: str,
        channel: str,
    ) -> int:
        """
        In the final implementation, this will:
        - Normalize `from` and `to` into contacts
        - Determine which one is the customer-owned identity
        - Look up or create a long-lived conversation
        For now we simply return a placeholder id.
        """
        # TODO: implement real conversation grouping in Commit 3
        return 1

    def list_conversations(self, db) -> list[dict]:
        """
        Will return summaries from the database. For now, returns a single fake conversation.
        """
        from datetime import datetime
        return [
            {
                "id": 1,
                "last_updated": datetime.utcnow(),
            }
        ]

    def list_messages_for_conversation(self, db, conversation_id: int) -> list[dict]:
        """
        Will return messages for a given conversation. For now, returns an empty list.
        """
        return []
