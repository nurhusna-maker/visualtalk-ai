import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="VisualTalk AI Lite", page_icon="🎙️", layout="wide")

components.html(
"""
<!DOCTYPE html>
<html>
<head>
<style>
body {
  font-family: Arial, sans-serif;
  background: #ffffff;
  color: #222;
}
.container {
  max-width: 1050px;
  margin: auto;
  padding: 20px;
}
h1 {
  font-size: 46px;
  margin-bottom: 5px;
}
.subtitle {
  color: #666;
  font-size: 18px;
  margin-bottom: 25px;
}
.card {
  border: 1px solid #ddd;
  border-radius: 16px;
  padding: 22px;
  margin-bottom: 20px;
  background: #fafafa;
}
button {
  padding: 12px 20px;
  border-radius: 10px;
  border: 1px solid #888;
  background: #f4f4f4;
  cursor: pointer;
  font-size: 16px;
  margin: 5px;
}
button:hover {
  background: #e8e8e8;
}
textarea {
  width: 100%;
  min-height: 180px;
  font-size: 16px;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid #aaa;
}
.feedback {
  background: #eef7ee;
  border-left: 6px solid #4CAF50;
  padding: 16px;
  border-radius: 10px;
  margin-top: 15px;
}
.warning {
  background: #fff3cd;
  border-left: 6px solid #ffc107;
  padding: 14px;
  border-radius: 10px;
}
img {
  max-width: 100%;
  border-radius: 12px;
  margin-top: 10px;
}
.score {
  font-size: 22px;
  font-weight: bold;
}
.small {
  color: #666;
  font-size: 14px;
}
</style>
</head>

<body>
<div class="container">
  <h1>🎙️ VisualTalk AI Lite</h1>
  <div class="subtitle">Free AI-assisted visual description practice tool</div>

  <div class="warning">
    This free version uses your browser's speech recognition. It works best in Google Chrome.
    No OpenAI API key is needed.
  </div>

  <div class="card">
    <h2>1. Upload Your Visual</h2>
    <input type="file" id="imageInput" accept="image/*">
    <br>
    <img id="preview">
  </div>

  <div class="card">
    <h2>2. Record or Dictate Your Speech</h2>
    <p>Click <b>Start Speaking</b>, describe the visual, then click <b>Stop</b>.</p>
    <button onclick="startRecognition()">🎤 Start Speaking</button>
    <button onclick="stopRecognition()">⏹ Stop</button>
    <button onclick="clearText()">🧹 Clear</button>
    <p class="small" id="status">Status: Ready</p>

    <textarea id="transcript" placeholder="Your speech transcript will appear here. You may also type or paste your answer."></textarea>
  </div>

  <div class="card">
    <h2>3. Get Feedback</h2>
    <button onclick="analyseSpeaking()">Analyse My Speaking</button>
    <div id="feedback"></div>
  </div>
</div>

<script>
let recognition;
let finalTranscript = "";

document.getElementById("imageInput").addEventListener("change", function(event) {
  const file = event.target.files[0];
  if (file) {
    document.getElementById("preview").src = URL.createObjectURL(file);
  }
});

function startRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    document.getElementById("status").innerText = "Status: Speech recognition is not supported in this browser. Please use Google Chrome.";
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  recognition.onstart = function() {
    document.getElementById("status").innerText = "Status: Listening...";
  };

  recognition.onresult = function(event) {
    let interimTranscript = "";
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript + " ";
      } else {
        interimTranscript += event.results[i][0].transcript;
      }
    }
    document.getElementById("transcript").value = finalTranscript + interimTranscript;
  };

  recognition.onerror = function(event) {
    document.getElementById("status").innerText = "Status: Error - " + event.error;
  };

  recognition.onend = function() {
    document.getElementById("status").innerText = "Status: Stopped";
  };

  recognition.start();
}

function stopRecognition() {
  if (recognition) {
    recognition.stop();
  }
}

function clearText() {
  finalTranscript = "";
  document.getElementById("transcript").value = "";
  document.getElementById("feedback").innerHTML = "";
}

function countWords(text) {
  return text.trim().split(/\\s+/).filter(Boolean).length;
}

function countSentences(text) {
  const matches = text.match(/[.!?]+/g);
  return matches ? matches.length : Math.max(1, Math.round(countWords(text)/15));
}

function vocabularyScore(text) {
  const words = text.toLowerCase().match(/\\b[a-z]+\\b/g) || [];
  const unique = new Set(words);
  if (words.length === 0) return 0;
  const ratio = unique.size / words.length;
  return Math.min(10, Math.round(ratio * 18));
}

function organisationScore(text) {
  const markers = ["first", "second", "next", "then", "after that", "finally", "overall", "in conclusion", "on the left", "on the right", "in the background", "in the foreground"];
  let score = 4;
  markers.forEach(m => {
    if (text.toLowerCase().includes(m)) score += 1;
  });
  return Math.min(10, score);
}

function contentScore(wordCount) {
  if (wordCount >= 120) return 10;
  if (wordCount >= 90) return 8;
  if (wordCount >= 60) return 6;
  if (wordCount >= 30) return 4;
  if (wordCount > 0) return 2;
  return 0;
}

function fluencyScore(text, wordCount) {
  const fillers = ["um", "uh", "erm", "like like", "you know"];
  let score = contentScore(wordCount);
  fillers.forEach(f => {
    if (text.toLowerCase().includes(f)) score -= 1;
  });
  return Math.max(1, Math.min(10, score));
}

function grammarScore(text) {
  let score = 8;
  const lower = text.toLowerCase();
  const issues = ["he are", "she are", "they is", "people is", "i is", "many person", "much people"];
  issues.forEach(i => {
    if (lower.includes(i)) score -= 1;
  });
  return Math.max(3, score);
}

function analyseSpeaking() {
  const text = document.getElementById("transcript").value.trim();
  const feedbackDiv = document.getElementById("feedback");

  if (!text) {
    feedbackDiv.innerHTML = "<div class='feedback'>Please record, type, or paste your response first.</div>";
    return;
  }

  const words = countWords(text);
  const sentences = countSentences(text);
  const avgSentence = Math.round(words / sentences);

  const content = contentScore(words);
  const vocab = vocabularyScore(text);
  const organisation = organisationScore(text);
  const fluency = fluencyScore(text, words);
  const grammar = grammarScore(text);
  const total = content + vocab + organisation + fluency + grammar;

  let strengths = [];
  let improve = [];

  if (words >= 90) strengths.push("Your response has sufficient length and detail.");
  else improve.push("Try to give a longer response with more details about the visual.");

  if (organisation >= 7) strengths.push("You used some organising words or spatial descriptions.");
  else improve.push("Use phrases such as 'on the left', 'in the background', 'first', 'next', and 'overall'.");

  if (vocab >= 7) strengths.push("You used a fair range of vocabulary.");
  else improve.push("Use more descriptive adjectives and specific nouns.");

  if (avgSentence > 22) improve.push("Some sentences may be too long. Try shorter and clearer sentences.");

  const improvedTemplate = `
Good morning. In this visual, I can see a busy place with several people and clear activities. 
In the foreground, there are people who seem to be moving or waiting. 
In the background, there are important details that help explain the setting. 
The visual suggests that the place is active, organised, and connected to daily life. 
Overall, this picture shows an interesting situation because it includes people, objects, and a clear environment.
  `;

  feedbackDiv.innerHTML = `
    <div class="feedback">
      <div class="score">Overall Score: ${total}/50</div>
      <br>
      <b>Content and Visual Description:</b> ${content}/10<br>
      <b>Organisation:</b> ${organisation}/10<br>
      <b>Vocabulary:</b> ${vocab}/10<br>
      <b>Grammar:</b> ${grammar}/10<br>
      <b>Fluency:</b> ${fluency}/10<br>
      <br>
      <b>Word Count:</b> ${words}<br>
      <b>Estimated Sentences:</b> ${sentences}<br>
      <b>Average Sentence Length:</b> ${avgSentence} words<br>
      <br>
      <b>Strengths:</b>
      <ul>${strengths.map(s => "<li>" + s + "</li>").join("") || "<li>You attempted to describe the visual.</li>"}</ul>
      <b>Areas to Improve:</b>
      <ul>${improve.map(s => "<li>" + s + "</li>").join("") || "<li>Continue practising with different visuals.</li>"}</ul>
      <b>Suggested Response Structure:</b>
      <p>${improvedTemplate}</p>
    </div>
  `;
}
</script>
</body>
</html>
""",
height=1300,
scrolling=True,
)