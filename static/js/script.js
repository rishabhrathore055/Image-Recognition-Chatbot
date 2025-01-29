document.addEventListener("DOMContentLoaded", function () {
  // Get references to elements
  const sendBtn = document.getElementById("send-btn");
  const micBtn = document.getElementById("mic-btn");
  const userInput = document.getElementById("user-input");
  const imageUpload = document.getElementById("image-upload");
  const generateCaptionBtn = document.getElementById("generate-caption-btn");
  const chatBox = document.getElementById("chat-box");

  if (!micBtn) {
    console.error("❌ mic-btn element not found!");
    return;
  }

  if (!generateCaptionBtn) {
    console.warn(
      "⚠️ generate-caption-btn not found! Skipping caption feature."
    );
  }

  let uploadedImage = null; // Store uploaded image

  // Function to append messages to the chat box
  function addMessage(content, sender = "bot") {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    messageDiv.innerHTML = content;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the bottom
  }

  // Handle image upload
  imageUpload.addEventListener("change", async () => {
    const file = imageUpload.files[0];
    if (!file) return;

    uploadedImage = file;
    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await fetch("/upload", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Image upload failed.");

      const data = await response.json();
      addMessage(
        `<img src="${URL.createObjectURL(
          file
        )}" alt="Uploaded Image" style="max-width: 200px; border-radius: 8px;">`
      );
    } catch (err) {
      addMessage("❌ Failed to upload image.");
      console.error(err);
    }
  });

  // Handle text queries
  sendBtn.addEventListener("click", async () => {
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(`🧑‍💻 You: ${message}`, "user");
    userInput.value = "";

    if (!uploadedImage) {
      addMessage("⚠️ Please upload image");
      return;
    }

    try {
      const response = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) throw new Error("Failed to process request.");
      const data = await response.json();
      addMessage(`🤖 ${data.reply || "No relevant information found."}`);
    } catch (err) {
      addMessage("❌ Error processing request.");
      console.error(err);
    }
  });

  // Handle caption generation (only if button exists)
  if (generateCaptionBtn) {
    generateCaptionBtn.addEventListener("click", async () => {
      if (!uploadedImage) {
        addMessage("⚠️ Upload an image you want to know about");
        return;
      }

      try {
        const response = await fetch("/generate_caption", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });

        if (!response.ok) throw new Error("Failed to generate caption.");
        const data = await response.json();
        addMessage(`📸 Caption: ${data.caption || "N/A"}`);
      } catch (err) {
        addMessage("❌ Caption generation failed.");
        console.error(err);
      }
    });
  }

  // Web Speech API for Voice Input
  if (!("webkitSpeechRecognition" in window)) {
    alert(
      "⚠️ Your browser does not support speech recognition. Please use Chrome!"
    );
  } else {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    micBtn.addEventListener("click", () => {
      try {
        console.log("🎤 Mic button clicked"); // Debugging
        micBtn.disabled = true;
        addMessage("🎤 Listening...");
        recognition.start();
      } catch (error) {
        addMessage("❌ Voice recognition error.");
        console.error("Speech recognition error:", error);
        micBtn.disabled = false;
      }
    });

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log("Voice detected:", transcript); // Debugging
      userInput.value = transcript;
      addMessage(`🗣️ You said: "${transcript}"`, "user");
      sendBtn.click(); // Auto-send voice query
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      addMessage("❌ Voice recognition error. Try again.");
      micBtn.disabled = false;
    };

    recognition.onend = () => {
      console.log("🎤 Recognition ended"); // Debugging
      micBtn.disabled = false;
    };
  }

  console.log("✅ Script loaded successfully!");
});
