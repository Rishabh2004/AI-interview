from app.core.config import get_settings
from elevenlabs import (
    AgentConfigDbModel,
    ConversationSimulationSpecification,
    ElevenLabs,
    ArrayJsonSchemaPropertyInput  # Make sure this is imported
)

# Explicitly rebuild the model if needed
AgentConfigDbModel.model_rebuild()

settings = get_settings()

client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

# # Get agent information
# agent = client.conversational_ai.get_agent(
#     agent_id="agent_01jvkxeh5sfteta3wc6v4adhzm",
# )

# Simulate a conversation using the correct model classes
simulation = client.conversational_ai.agents.simulate_conversation_stream(
    agent_id="agent_01jvkxeh5sfteta3wc6v4adhzm",
    simulation_specification=ConversationSimulationSpecification(
        simulated_user_config=AgentConfigDbModel(
            first_message="Hello, how can I help you today?",
            language="en",
        ),
    ),
)

print("Simulation================>:", simulation)