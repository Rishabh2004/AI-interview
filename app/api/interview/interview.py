from typing import Optional, Dict, Any
from app.api.interview.voice import VoiceService
from app.core.config import get_settings
from app.db.memory import add_memory, retrieve_memories
import signal
from elevenlabs.conversational_ai.conversation import ClientTools


settings = get_settings()

class InterviewService:
    def __init__(self):
        self.voice_service = VoiceService()
        self._register_tools()
    
    def _register_tools(self):
        """Register memory tools with the client"""

        async def add_memories(parameters: Dict[str, Any]):
            user_id = parameters.get("user_id", settings.DEFAULT_USER_ID)
            message = parameters.get("message", "")
            success = await add_memory(user_id, message)
            return "Memory added successfully" if success else "Failed to add memory"

        async def retrieve_user_memories(parameters: Dict[str, Any]):
            user_id = parameters.get("user_id", settings.DEFAULT_USER_ID)
            query = parameters.get("message", "")
            memories = await retrieve_memories(user_id, query)
            return "\n".join(m["memory"] for m in memories) if memories else "No relevant memories found"
        pass
    
    async def conduct_interview(self, user_id: Optional[str] = None):
        """Conduct a simple interview session"""
        user_id = user_id or settings.DEFAULT_USER_ID

        print(f"Starting interview with user {user_id}")

       # Define the resume memory tool as an async function
        async def resume_memory_tool(parameters: Dict[str, Any]) -> str:
            resume_query = "Retrieve all resume information for the interview"
            resume_data = await retrieve_memories(user_id, resume_query, limit=20)

            if not resume_data:
                return "No resume information found for the user."

            return "\n".join([m["memory"] for m in resume_data])

        # Create client tools and register the resume memory tool
        client_tools = ClientTools()
        client_tools.register("ResumeMemoryTool", resume_memory_tool, is_async=True)

        # Create the voice conversation with tools
        conversation = self.voice_service.create_conversation(
            agent_id=settings.AGENT_ID,
            client_tools=client_tools,
            callback_agent_response=None,
            callback_user_transcript=None
        )

        # Start session with an initial prompt to instruct the agent
        conversation.start_session()

        # Handle Ctrl+C to gracefully end the session
        signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())
        # Wait for conversation to complete
        conversation_id = conversation.wait_for_session_end()

        print(f"Interview completed. Conversation ID: {conversation_id}")
        return {"status": "completed", "conversation_id": conversation_id}
