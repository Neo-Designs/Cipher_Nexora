document.getElementById("send-btn").addEventListener("click", () => {
    const introInput = document.getElementById("user-input").value.trim();
    if (!introInput) return;

    startChatWithMessage(introInput);
});

document.getElementById("user-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        document.getElementById("send-btn").click();
    }
});

function startChatWithMessage(message) {
    document.querySelector(".intro").classList.add("hidden");
    document.querySelector(".chat-container").classList.remove("hidden");

    appendMessage(message, "user");
    sendToServer(message);
}

document.getElementById("chat-send-btn").addEventListener("click", () => {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    input.value = "";
    sendToServer(message);
});

document.getElementById("chat-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        document.getElementById("chat-send-btn").click();
    }
});

function appendMessage(message, role) {
    const chatBox = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.className = `message ${role}`;
    msg.textContent = message;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendToServer(message) {
    const typingIndicator = document.getElementById("typing-indicator");
    typingIndicator.classList.remove("hidden");

    fetch("/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    })
    .then(res => {
        return res.json();
    })
    .then(data => {
        typingIndicator.classList.add("hidden");
        appendMessage(data.response, "assistant");
    })
    .catch(err => {
        typingIndicator.classList.add("hidden");
        appendMessage("Oops! Something glitched (maybe Vexora?). Try again!", "assistant");
    });
}

window.onload = function () {
    const introRecognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    introRecognition.lang = 'en-US';
    introRecognition.continuous = false;
    introRecognition.interimResults = false;

    const micBtn = document.getElementById('micBtn');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    micBtn.addEventListener('click', () => {
        console.log("🎙️ Listening (intro)...");
        introRecognition.start();
    });

    introRecognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        console.log("🗣️ Intro Voice:", transcript);
        userInput.value = transcript;
        sendBtn.click();
    };

    introRecognition.onerror = function (event) {
        console.error("🚨 Intro Voice Error:", event.error);
    };

    const chatRecognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    chatRecognition.lang = 'en-US';
    chatRecognition.continuous = false;
    chatRecognition.interimResults = false;

    const voiceBtn = document.getElementById('voice-btn');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');

    voiceBtn.addEventListener('click', () => {
        console.log("🎙️ Listening (chat)...");
        chatRecognition.start();
    });

    chatRecognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        console.log("🗣️ Chat Voice:", transcript);
        chatInput.value = transcript;
        chatSendBtn.click();
    };

    chatRecognition.onerror = function (event) {
        console.error("🚨 Chat Voice Error:", event.error);
    };
};


document.addEventListener("DOMContentLoaded", () => {
    const mode = localStorage.getItem("darkMode");
    if (mode === "disabled") {
        document.body.classList.add("light-mode");
    }

    const toggleBtn = document.getElementById("darkModeToggle");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            document.body.classList.toggle("light-mode");

            const newMode = document.body.classList.contains("light-mode") ? "disabled" : "enabled";
            localStorage.setItem("darkMode", newMode);
        });
    }
});
