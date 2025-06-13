const getSuggestions = async () => {
    try {
        const moodInput = document.getElementById('moodInput').value;
        if (!moodInput) {
            return;
        }

        const response = await fetch('/api/suggestion', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                moodInput
            })
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();

        const moodEmoji = {
            "sadness": "😔",
            "joy": "😊",
            "love": "❤️",
            "anger": "😤",
            "fear": "😨",
            "surprise": "😲"
        }

        document.getElementById('mood').innerHTML = moodEmoji[data.mood] + " " + data.mood;
        document.getElementById("song").innerHTML = data.song.name;
        document.getElementById("artist").innerHTML = data.song.artist;
        document.getElementById("link").href = data.song.url;

        document.getElementById('moodContainer').style.display = "flex";
        document.getElementById('moodContainer').style.flexDirection = "column";
    }
    catch (error) {
        console.error('Error fetching suggestions:', error);
        return;
    }
}