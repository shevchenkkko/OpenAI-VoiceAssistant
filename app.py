import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
import base64
from dotenv import load_dotenv

load_dotenv()


def transcribe_audio(client, audio_path):
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file)
        return transcript.text


def fetch_ai_response(client, input_text):
    messages = [{"role": "user", "content": input_text}]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content


def text_to_speech(client, text, audio_path):
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="echo",
        input=text,
    ) as response:
        response.stream_to_file(audio_path)


def create_text_card(text, title="Response"):
    card_html = f"""
    <style>
        .card {{
            box-shadow: 4px 8px 0 rgba(0,0,0,0.2);
            transition: 0.3s;
            border-radius: 5px;
            padding: 15px;
        }}
        .card:hover {{
            box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        }}
        .container{{
            padding:2px 16px;
        }}
    </style>
    <div class='card'>
        <div class='container'>
            <h4><b>{title}</b></h4>
            <p>{text}</p>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def auto_play_audio(audio_file):
    with open(audio_file, 'rb') as audio_file:
        audio_bytes = audio_file.read()
    base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay hidden>'
    st.markdown(audio_html, unsafe_allow_html=True)


def main():
    st.title('Your Voice Assistant')
    st.write('Hi! Click on the voice recorder to interact with me.')
    client = openai.OpenAI()

    recorded_audio = audio_recorder()

    if recorded_audio:
        audio_file = 'audio.mp3'
        with open(audio_file, 'wb') as f:
            f.write(recorded_audio)
        transcribed_text = transcribe_audio(client, audio_file)
        create_text_card(transcribed_text, "Transcribed text")

        ai_response = fetch_ai_response(client, transcribed_text)

        response_audio_file = 'audio_response.mp3'
        text_to_speech(client, ai_response, response_audio_file)
        auto_play_audio(response_audio_file)
        create_text_card(ai_response, "AI Response")


if __name__ == '__main__':
    main()
