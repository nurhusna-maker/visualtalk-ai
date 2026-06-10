import streamlit as st
from openai import OpenAI
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="VisualTalk AI", page_icon="🎙️", layout="centered")

st.title("🎙️ VisualTalk AI")
st.caption("AI-Assisted Visual Description Practice Tool")

st.write("""
Upload a visual, record your speaking response, and receive feedback on your visual description.
""")

# API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.subheader("1. Upload Your Visual")
uploaded_image = st.file_uploader("Upload a picture/visual", type=["jpg", "jpeg", "png"])

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Visual", use_container_width=True)

st.subheader("2. Record Your Speech")
audio_file = st.audio_input("Record your response here")

st.subheader("3. Get AI Feedback")

if st.button("Analyse My Speaking"):
    if not uploaded_image:
        st.error("Please upload a visual first.")
    elif not audio_file:
        st.error("Please record your speech first.")
    else:
        with st.spinner("Transcribing your speech..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                tmp_audio.write(audio_file.read())
                audio_path = tmp_audio.name

            with open(audio_path, "rb") as audio:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio
                )

            student_text = transcript.text

        st.subheader("Your Transcript")
        st.write(student_text)

        with st.spinner("Generating feedback..."):
            prompt = f"""
You are an English speaking assessment coach for Malaysian diploma students.

The student described a visual orally. Give constructive feedback using this format:

1. Content and Visual Description
2. Organisation of Ideas
3. Vocabulary
4. Grammar and Sentence Structure
5. Fluency and Clarity
6. Strengths
7. Areas to Improve
8. Suggested Improved Response

Be supportive, clear, and suitable for students.

Student transcript:
{student_text}
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful English speaking coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )

        st.subheader("AI Feedback")
        st.write(response.choices[0].message.content)

        os.remove(audio_path)

st.divider()
st.caption("Developed as a prototype for visual description speaking practice.")