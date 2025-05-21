from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation, ClientTools
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from app.core.config import get_settings

settings = get_settings()

class VoiceService:
    def __init__(self):
        self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        self.requires_auth = bool(settings.ELEVENLABS_API_KEY)
    
    def create_conversation(
        self,
        agent_id: str,
        client_tools: ClientTools,
        callback_agent_response: callable,
        callback_user_transcript: callable
    ) -> Conversation:
        """Create a new conversation with the AI agent"""
        return Conversation(
            self.client,
            agent_id,
            requires_auth=self.requires_auth,
            audio_interface=DefaultAudioInterface(),
            client_tools=client_tools,
            callback_agent_response=callback_agent_response,
            callback_user_transcript=callback_user_transcript,
        )
