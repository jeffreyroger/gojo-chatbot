const chatBox = document.getElementById("chat");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");

const SESSION_ID = crypto.randomUUID();

/* ---------- TIME ---------- */
function getTime() {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/* ---------- ADD USER MESSAGE ---------- */
function addUserMessage(text) {
  const msg = document.createElement("div");
  msg.className = "message user";

  msg.innerHTML = `
    <div class="text">${text}</div>
    <span class="timestamp">${getTime()}</span>
  `;

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

/* ---------- CREATE GOJO TYPING BUBBLE ---------- */
function createGojoTypingBubble() {
  const msg = document.createElement("div");
  msg.className = "message gojo";

  msg.innerHTML = `
    <img src="http://127.0.0.1:8000/static/gojo.jpg" class="avatar" />
    <div class="text">
      <span class="typing-dots">
        <span></span><span></span><span></span>
      </span>
    </div>
    <span class="timestamp">${getTime()}</span>
  `;

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;

  return msg.querySelector(".text");
}

/* ---------- CLEAN LLM TEXT ---------- */
function cleanLLMText(text) {
  text = text.replace(/([a-z])([A-Z])/g, "$1 $2")
             .replace(/([a-zA-Z])(\d)/g, "$1 $2")
             .replace(/(\d)([a-zA-Z])/g, "$1 $2");
  text = text.replace(/([,.!?])(?=\S)/g, "$1 ");
  return text.replace(/\s+/g, " ").trim();
}

/* ---------- STREAM INTO EXISTING GOJO BUBBLE ---------- */
async function streamIntoBubble(text, textDiv) {
  textDiv.innerHTML = "";

  for (let char of text) {
    textDiv.innerText += char;
    chatBox.scrollTop = chatBox.scrollHeight;
    await new Promise(r => setTimeout(r, 18));
  }
}

/* ---------- SEND MESSAGE ---------- */
async function sendMessage() {
  if (sendBtn.disabled) return;

  const text = input.value.trim();
  if (!text) return;

  addUserMessage(text);
  input.value = "";
  sendBtn.disabled = true;

  // Show Gojo typing bubble immediately
  const gojoTextDiv = createGojoTypingBubble();

  try {
    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: SESSION_ID
      })
    });

    if (!res.ok) throw new Error("Server error");

    const data = await res.json();
    const cleanText = cleanLLMText(data.reply);

    await streamIntoBubble(cleanText, gojoTextDiv);
  } catch (err) {
    gojoTextDiv.innerText = "…tch. Try again.";
    console.error(err);
  } finally {
    sendBtn.disabled = false;
  }
}

/* ---------- EVENTS ---------- */
sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});
