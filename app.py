import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="VisualTalk Lite Plus", page_icon="🎙️", layout="wide")

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
  max-width: 1100px;
  margin: auto;
  padding: 20px;
}
h1 {
  font-size: 44px;
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
  margin-bottom: 15px;
}
.blue {
  background: #eef5ff;
  border-left: 6px solid #3f7ddd;
  padding: 14px;
  border-radius: 10px;
  margin-bottom: 15px;
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
.timer {
  font-size: 34px;
  font-weight: bold;
  color: #333;
  margin: 10px 0;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
@media (max-width: 800px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
</head>

<body>
<div class="container">
  <h1>🎙️ VisualTalk Lite Plus</h1>
  <div class="subtitle">Free spontaneous visual description practice tool</div>

  <div class="warning">
    This version is 100% free. It uses browser speech recognition and rule-based feedback.
    It does not use OpenAI API, so it cannot truly analyse the image. Students must describe what they see clearly.
  </div>

  <div class="grid">
    <div class="card">
      <h2>1. Upload Visual</h2>
      <input type="file" id="imageInput" accept="image/*">
      <br>
      <img id="preview">
    </div>

    <div class="card">
      <h2>2. Speaking Timer</h2>
      <p>Recommended: 1 minute preparation + 2 minutes speaking.</p>
      <button onclick="startPrepTimer(60)">⏱ 1-Min Prep</button>
      <button onclick="startSpeakingTimer(120)">🎙 2-Min Speaking</button>
      <button onclick="resetTimer()">Reset Timer</button>
      <div class="timer" id="timerDisplay">Ready</div>
      <p class="small">Use the timer to encourage spontaneous speaking without writing a script.</p>
    </div>
  </div>

  <div class="card">
    <h2>3. Record / Dictate Speech</h2>
    <p>Click <b>Start Speaking</b>, describe the visual, then click <b>Stop</b>.</p>
    <button onclick="startRecognition()">🎤 Start Speaking</button>
    <button onclick="stopRecognition()">⏹ Stop</button>
    <button onclick="clearText()">🧹 Clear</button>
    <p class="small" id="status">Status: Ready</p>

    <textarea id="transcript" placeholder="Your speech transcript will appear here. You may also type or paste your answer."></textarea>
  </div>

  <div class="card">
    <h2>4. Get Feedback</h2>
    <button onclick="analyseSpeaking()">Analyse My Speaking</button>
    <div id="feedback"></div>
  </div>
</div>

<script>
let recognition;
let finalTranscript = "";
let timerInterval;

document.getElementById("imageInput").addEventListener("change", function(event) {
  const file = event.target.files[0];
  if (file) {
    document.getElementById("preview").src = URL.createObjectURL(file);
  }
});

function startPrepTimer(seconds) {
  startTimer(seconds, "Preparation");
}

function startSpeakingTimer(seconds) {
  startTimer(seconds, "Speaking");
}

function startTimer(seconds, label) {
  clearInterval(timerInterval);
  let remaining = seconds;
  const display = document.getElementById("timerDisplay");

  timerInterval = setInterval(function() {
    let min = Math.floor(remaining / 60);
    let sec = remaining % 60;
    display.innerText = label + ": " + min + ":" + (sec < 10 ? "0" : "") + sec;

    if (remaining <= 0) {
      clearInterval(timerInterval);
      display.innerText = label + " time is over";
    }
    remaining--;
  }, 1000);
}

function resetTimer() {
  clearInterval(timerInterval);
  document.getElementById("timerDisplay").innerText = "Ready";
}

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
    let message = event.error;
    if (event.error === "not-allowed") {
      message = "Microphone permission was denied. Please allow microphone access in Chrome settings.";
    }
    document.getElementById("status").innerText = "Status: Error - " + message;
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
  return matches ? matches.length : Math.max(1, Math.round(countWords(text)/14));
}

function containsAny(text, words) {
  const lower = text.toLowerCase();
  return words.some(w => lower.includes(w));
}

function vocabularyScore(text) {
  const words = text.toLowerCase().match(/\\b[a-z]+\\b/g) || [];
  const unique = new Set(words);
  if (words.length === 0) return 0;
  const ratio = unique.size / words.length;
  return Math.min(10, Math.round(ratio * 18));
}

function organisationScore(text) {
  const markers = [
    "first", "second", "next", "then", "after that", "finally", "overall",
    "in conclusion", "on the left", "on the right", "in the background",
    "in the foreground", "at the centre", "near", "beside", "behind",
    "in front of", "while", "whereas", "however"
  ];
  let score = 3;
  markers.forEach(m => {
    if (text.toLowerCase().includes(m)) score += 1;
  });
  return Math.min(10, score);
}

function contentScore(text, wordCount) {
  let score = 0;

  if (wordCount >= 120) score += 4;
  else if (wordCount >= 90) score += 3;
  else if (wordCount >= 60) score += 2;
  else if (wordCount >= 30) score += 1;

  if (containsAny(text, ["picture", "visual", "image", "scene", "photo"])) score += 1;
  if (containsAny(text, ["people", "person", "man", "woman", "student", "passenger", "worker", "children", "family"])) score += 1;
  if (containsAny(text, ["doing", "walking", "waiting", "talking", "sitting", "standing", "carrying", "looking", "working", "helping"])) score += 1;
  if (containsAny(text, ["background", "foreground", "left", "right", "centre", "behind", "beside", "near"])) score += 1;
  if (containsAny(text, ["busy", "calm", "crowded", "organised", "clean", "noisy", "peaceful", "serious", "happy"])) score += 1;
  if (containsAny(text, ["i think", "in my opinion", "this shows", "this reminds me", "overall"])) score += 1;

  return Math.min(10, score);
}

function fluencyScore(text, wordCount) {
  let score = wordCount >= 100 ? 9 : wordCount >= 70 ? 7 : wordCount >= 40 ? 5 : wordCount > 0 ? 3 : 0;
  const fillers = ["um", "uh", "erm", "like like", "you know"];
  fillers.forEach(f => {
    if (text.toLowerCase().includes(f)) score -= 1;
  });
  return Math.max(1, Math.min(10, score));
}

function grammarScore(text) {
  let score = 8;
  const lower = text.toLowerCase();
  const issues = ["he are", "she are", "they is", "people is", "i is", "many person", "much people", "many luggage", "many informations"];
  issues.forEach(i => {
    if (lower.includes(i)) score -= 1;
  });
  if (!/[.!?]/.test(text) && countWords(text) > 50) score -= 1;
  return Math.max(3, score);
}

function getBand(total) {
  if (total >= 41) return "Band 5";
  if (total >= 31) return "Band 4";
  if (total >= 21) return "Band 3";
  return "Band 2";
}

function buildStrengths(text, words, organisation, vocab) {
  let strengths = [];

  if (words >= 90) strengths.push("You gave a response with sufficient length.");
  if (containsAny(text, ["people", "person", "man", "woman", "student", "passenger", "worker", "children"])) strengths.push("You described the people in the visual.");
  if (containsAny(text, ["walking", "waiting", "talking", "sitting", "standing", "carrying", "working", "helping"])) strengths.push("You mentioned actions, which makes your description clearer.");
  if (containsAny(text, ["background", "foreground", "left", "right", "centre", "near", "behind"])) strengths.push("You used spatial description to organise your answer.");
  if (containsAny(text, ["i think", "in my opinion", "overall", "this shows", "this reminds me"])) strengths.push("You included your opinion or interpretation.");
  if (vocab >= 7) strengths.push("You used a reasonable range of vocabulary.");

  if (strengths.length === 0) strengths.push("You attempted to describe the visual. This is a good starting point.");

  return strengths;
}

function buildImprovements(text, words, avgSentence) {
  let improve = [];

  if (words < 60) improve.push("Try to speak longer. Add details about the place, people, objects, actions, and atmosphere.");
  if (!containsAny(text, ["background", "foreground", "left", "right", "centre", "near", "behind"])) improve.push("Use location phrases such as 'in the foreground', 'in the background', 'on the left', and 'on the right'.");
  if (!containsAny(text, ["busy", "calm", "crowded", "organised", "clean", "noisy", "peaceful", "serious", "happy"])) improve.push("Describe the atmosphere. For example: busy, calm, crowded, organised, cheerful, or serious.");
  if (!containsAny(text, ["i think", "in my opinion", "overall", "this shows", "this reminds me"])) improve.push("Add one opinion at the end. For example: 'I think this visual shows...' or 'This picture reminds me of...'");
  if (avgSentence > 22) improve.push("Some sentences may be too long. Use shorter and clearer sentences.");
  if (!containsAny(text, ["because", "while", "whereas", "although", "however"])) improve.push("Use connectors such as 'because', 'while', 'whereas', and 'overall' to make your answer smoother.");

  if (improve.length === 0) improve.push("Continue practising with different visuals and try to use more specific vocabulary.");

  return improve;
}

function buildVocabularySuggestions(text) {
  let suggestions = [
    "people → passengers / customers / visitors / students / workers",
    "things → objects / facilities / equipment / belongings",
    "place → location / setting / environment",
    "busy → crowded / lively / active",
    "good → suitable / useful / well-organised",
    "many → several / a number of / a group of",
    "walking → moving around / heading towards / passing by",
    "waiting → queuing / standing by / preparing",
    "background → behind them / at the back / further away",
    "overall → in general / all in all / to conclude"
  ];

  return suggestions;
}

function buildImprovedStructure() {
  return `
<b>Useful Speaking Structure:</b><br><br>

<b>1. Opening</b><br>
Good morning. This visual shows <i>[place/setting]</i>.<br><br>

<b>2. People</b><br>
I can see <i>[who]</i>. Some of them are <i>[action]</i>, while others are <i>[action]</i>.<br><br>

<b>3. Objects and Details</b><br>
In the foreground, there is/are <i>[object]</i>. In the background, I can see <i>[object/place]</i>.<br><br>

<b>4. Atmosphere</b><br>
The place looks <i>[busy/calm/crowded/organised]</i> because <i>[reason]</i>.<br><br>

<b>5. Opinion</b><br>
Overall, I think this visual shows <i>[main idea]</i> because <i>[reason]</i>.
  `;
}

function buildSentencePatterns() {
  return `
<ul>
<li>This visual shows a scene at <b>[place]</b>.</li>
<li>In the foreground, I can see <b>[people/object]</b>.</li>
<li>In the background, there are <b>[objects/details]</b>.</li>
<li>Some people are <b>[action]</b>, while others are <b>[action]</b>.</li>
<li>The atmosphere seems <b>[adjective]</b> because <b>[reason]</b>.</li>
<li>Overall, I think this picture shows <b>[opinion/main idea]</b>.</li>
</ul>
  `;
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

  const content = contentScore(text, words);
  const vocab = vocabularyScore(text);
  const organisation = organisationScore(text);
  const fluency = fluencyScore(text, words);
  const grammar = grammarScore(text);
  const total = content + vocab + organisation + fluency + grammar;
  const band = getBand(total);

  const strengths = buildStrengths(text, words, organisation, vocab);
  const improve = buildImprovements(text, words, avgSentence);
  const vocabSuggestions = buildVocabularySuggestions(text);

  feedbackDiv.innerHTML = `
    <div class="feedback">
      <div class="score">Overall Score: ${total}/50 — ${band}</div>
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

      <b>What You Did Well:</b>
      <ul>${strengths.map(s => "<li>" + s + "</li>").join("")}</ul>

      <b>What To Improve:</b>
      <ul>${improve.map(s => "<li>" + s + "</li>").join("")}</ul>

      <b>Vocabulary Upgrade:</b>
      <ul>${vocabSuggestions.map(s => "<li>" + s + "</li>").join("")}</ul>

      <b>Better Sentence Patterns:</b>
      ${buildSentencePatterns()}

      <div class="blue">
        ${buildImprovedStructure()}
      </div>

      <b>Teacher Note:</b>
      <p>This free version gives feedback based on the student's transcript. It does not analyse the image automatically. 
      For better feedback, students should mention specific visual details clearly in their speech.</p>
    </div>
  `;
}
</script>
</body>
</html>
""",
height=1600,
scrolling=True,
)
