document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("tts-form");
    const audioPlayer = document.getElementById("audio-player");
    const audioSource = document.getElementById("audio-source");

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(form);

        fetch("/pronounce", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.audio_url) {
                audioSource.src = data.audio_url;
                audioPlayer.load();
                audioPlayer.play();
            }
        })
        .catch(error => console.error("Error:", error));
    });
});