document.addEventListener("DOMContentLoaded", () => {
    const audioFileInput = document.getElementById("audioFile");
    const messageInput = document.getElementById("messageInput");
    const encodeButton = document.getElementById("encodeButton");
    const decodeButton = document.getElementById("decodeButton");
    const algorithmSelect = document.getElementById("algorithmSelect");
    const statusMessage = document.getElementById("statusMessage");

    encodeButton.addEventListener("click", encodeAudio);
    decodeButton.addEventListener("click", decodeAudio);

    async function encodeAudio() {
        const file = audioFileInput.files[0];
        const message = messageInput.value.trim();
        const algorithm = algorithmSelect.value;

        if (!file || !message) {
            updateStatus("❌ Please select an audio file and enter a message.", "red");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("message", message);
        formData.append("algorithm", algorithm);

        try {
            const response = await fetch("http://127.0.0.1:5000/encode", {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            if (response.ok) {
                createDownloadLink(result.download_url);
                updateStatus("✅ Encoding successful! Download your file below.", "green");
            } else {
                updateStatus(`❌ Error: ${result.error}`, "red");
            }
        } catch (error) {
            updateStatus("❌ Encoding failed. Server error.", "red");
        }
    }

    async function decodeAudio() {
        const file = audioFileInput.files[0];
        const algorithm = algorithmSelect.value;

        if (!file) {
            updateStatus("❌ Please select an encoded audio file.", "red");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("algorithm", algorithm);

        try {
            const response = await fetch("http://127.0.0.1:5000/decode", {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            if (response.ok) {
                updateStatus(`✅ Decoding successful! Message: "${result.message}"`, "green");
            } else {
                updateStatus(`❌ Error: ${result.error}`, "red");
            }
        } catch (error) {
            updateStatus("❌ Decoding failed. Server error.", "red");
        }
    }

    function updateStatus(message, color) {
        statusMessage.textContent = message;
        statusMessage.style.color = color;
    }

    function createDownloadLink(downloadUrl) {
        const downloadLink = document.createElement("a");
        downloadLink.href = downloadUrl;
        downloadLink.textContent = "📥 Download Encoded File";
        downloadLink.style.color = "blue";
        downloadLink.style.display = "block";
        statusMessage.appendChild(document.createElement("br"));
        statusMessage.appendChild(downloadLink);
    }
});
