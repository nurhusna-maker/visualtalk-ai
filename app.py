import base64
import io
import tempfile
import time

import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder


st.set_page_config(
    page_title="VisualTalk AI V2",
    page_icon="🎙️",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 0px;
}
.subtitle {
    font-size: 18px;
    color: #666666;
    margin-bottom: 25px;
}
.box {
    border: 1px solid #dddddd;
    border-radius: 14px;
    padding: 18px;
    background-color: #fafafa;
    margin-bottom: 18px;
}
.small-note {
    color: #666666;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🎙️ VisualTalk AI V2</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Spontaneous visual description practice with AI feedback</div>", unsafe_allow_html=True)

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Please add your OpenAI API key in .streamlit/secrets.toml")
    st.stop()


def encode_image(uploaded_image):
    image_bytes = uploaded_image.getvalue()
    return base64.b64encode(image_bytes).decode("utf-8")


def transcribe_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    with open(temp_audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    return transcript.text


def analyse_visual_and_speech(image_base64, transcript_text, target_level, speaking_time):
    prompt = f"""
You are VisualTalk AI, an English speaking coach for Malaysian diploma students.

The student completed a spontaneous visual description task.

Target student level: {target_level}
Expected speaking time: {speaking_time}

Student transcript:
{transcript_text}

Analyse the uploaded visual and compare it with the student's speech.

IMPORTANT:
- Do not give generic feedback.
- Refer to actual visible details in the image.
- If the student misses important image details, name those details clearly.
- Keep the language student-friendly.
- Do not be too harsh.
- Use Malaysian diploma speaking assessment style.

Give the feedback using this exact format:

## 1. Visual Summary
Briefly identify the setting, people, objects, actions, and atmosphere in the picture.

## 2. What You Did Well
Give 3 specific strengths based on the transcript.

## 3. Important Details You Missed
Give 3 to 5 specific visual details that the student could add.

## 4. Vocabulary Upgrade
Give 10 useful words or phrases related to the visual.
Use this format:
- simple word → better word/phrase

## 5. Grammar and Sentence Improvement
Select up to 5 sentences or phrases from the student's transcript and improve them.
Use this format:
- Original:
- Improved:

If the transcript is too short, give general sentence patterns instead.

## 6. Organisation Feedback
Comment on whether the student described:
- place
- people
- objects
- actions
- atmosphere
- opinion

## 7. Suggested Improved Answer
Write an improved spontaneous answer suitable for the student's level.
It must be specific to the image.
Length:
- Band 3: 80-100 words
- Band 4: 120-150 words
- Band 5: 170-220 words

## 8. Estimated Speaking Band
Give:
- Content /10
- Organisation /10
- Vocabulary /10
- Grammar /10
- Fluency /10
- Total /50
- Estimated band: Band 3, Band 4, or Band 5

## 9. Next Practice Target
Give one clear target for the next practice.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
        ],
    )

    return response.output_text


with st.sidebar:
    st.header("Settings")
    target_level = st.selectbox(
        "Target level",
        ["Band 3", "Band 4", "Band 5"],
        index=1
    )

    prep_time = st.selectbox(
        "Preparation time",
        ["30 seconds", "1 minute", "2 minutes"],
        index=1
    )

    speaking_time = st.selectbox(
        "Speaking time",
        ["1 minute", "2 minutes", "3 minutes"],
        index=1
    )

    st.markdown("---")
    st.caption("Recommended for LCC002: 1 minute preparation + 2 minutes speaking.")


col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.subheader("1. Upload Visual")
    image = st.file_uploader(
        "Upload the visual for speaking practice",
        type=["jpg", "jpeg", "png"]
    )

    if image:
        st.image(image, caption="Student visual", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.subheader("2. Spontaneous Speaking Task")

    st.write("Instructions for students:")
    st.info(
        "Look at the visual. Prepare briefly. Then click **Start Speaking** and describe the picture spontaneously. "
        "Do not read from a script."
    )

    if image:
        if st.button("Start Preparation Timer"):
            seconds = {"30 seconds": 30, "1 minute": 60, "2 minutes": 120}[prep_time]
            timer_placeholder = st.empty()
            for remaining in range(seconds, 0, -1):
                timer_placeholder.warning(f"Preparation time left: {remaining} seconds")
                time.sleep(1)
            timer_placeholder.success("Preparation time is over. Start speaking now.")

        audio = mic_recorder(
            start_prompt="🎙️ Start Speaking",
            stop_prompt="⏹️ Stop Recording",
            just_once=True,
            use_container_width=True,
            key="visualtalk_recorder"
        )

        st.markdown(
            "<div class='small-note'>If recording is blocked, check browser microphone permission and use Google Chrome.</div>",
            unsafe_allow_html=True
        )
    else:
        audio = None
        st.warning("Please upload a visual first.")
    st.markdown("</div>", unsafe_allow_html=True)


if image and audio:
    st.markdown("---")
    st.subheader("3. AI Analysis")

    if st.button("Analyse My Speaking", type="primary"):
        with st.spinner("Transcribing your speech..."):
            audio_bytes = audio["bytes"]
            transcript_text = transcribe_audio(audio_bytes)

        st.subheader("Your Transcript")
        st.write(transcript_text)

        with st.spinner("Analysing the visual and your speech..."):
            image_base64 = encode_image(image)
            feedback = analyse_visual_and_speech(
                image_base64,
                transcript_text,
                target_level,
                speaking_time
            )

        st.subheader("AI Feedback")
        st.markdown(feedback)

elif image:
    st.markdown("---")
    st.info("After recording, click **Analyse My Speaking** to receive feedback.")
