from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
from app.core.config import get_settings
import sounddevice as sd
import assemblyai as aai
from openai import OpenAI
import soundfile as sf

settings = get_settings()
client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

def record_audio(filename="user_input.wav", duration=5, fs=44100):
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    sf.write(filename, audio, fs)
    print("Recording saved.")

def transcribe_audio(filename="user_input.wav"):
    aai.settings.api_key = settings.ASSEMBLYAI_API_KEY  # Add this to your config
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(filename)
    return transcript.text

def get_llm_response(prompt):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def play_audio(filename):
    data, fs = sf.read(filename, dtype='float32')
    sd.play(data, fs)
    sd.wait()

def dynamic_interview():
    while True:
        record_audio()
        user_text = transcribe_audio()
        print("User said:", user_text)
        llm_reply = get_llm_response(user_text)
        print("LLM says:", llm_reply)
        
        audio = client.text_to_speech.convert(
            text=llm_reply,
            voice_id="cgSgspJ2msm6clMCkdW9",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        with open("llm_reply.mp3", "wb") as f:
            for chunk in audio:
                f.write(chunk)
        print("LLM reply saved to llm_reply.mp3")
        play_audio("llm_reply.mp3")
        print("Press Ctrl+C to exit or speak again...")

if __name__ == "__main__":
    dynamic_interview()