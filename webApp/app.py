# Importing required functions 
from flask import Flask, request, render_template, jsonify
import re
import pickle
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os

model_path = os.path.join(os.path.dirname(__file__), 'model', 'emotion_detector.pkl')
vectorizer_path = os.path.join(os.path.dirname(__file__), 'model', 'vectorizer_emotion.pkl')

data_path = os.path.join(os.path.dirname(__file__), 'data', 'data_moods.csv')

# Use pickle to load in the pre-trained model.
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# Use pickle to load in vectorizer.
with open(vectorizer_path, 'rb') as f:
    vectorizer = pickle.load(f)

# instance of flask application
app = Flask(__name__)

emotions=["sadness", "joy", "love", "anger", "fear", "surprise"] #emotions list detected from the text

# Loading only required columns from the songs dataset
columns_needed = ['name', 'album', 'artist', 'id', 'release_date', 'popularity', 'mood']
songsData = pd.read_csv(data_path, usecols=columns_needed)

# print(songsData.head())  # Displaying the first few rows of the dataset
# Map Emotion → Mood
emotion_to_mood = {
    "sadness": "Sad",
    "joy": "Happy",
    "love": "Calm",
    "anger": "Energetic",
    "fear": "Calm",
    "surprise": "Energetic"
}

def get_song_by_emotion(emotion):
    mood = emotion_to_mood.get(emotion, "Calm")
    
    # Step 3: Filter songs by mood
    filtered_songs = songsData[songsData['mood'] == mood]

    if filtered_songs.empty:
        return "No songs found for mood:", mood

    # Step 4 (Optional): Sort by popularity or energy
    filtered_songs = filtered_songs.sort_values(by='popularity', ascending=False)

    # Step 5: Pick a random top N song
    top_songs = filtered_songs.head(10)
    selected_song = top_songs.sample(1).iloc[0]

    return {
        "name": selected_song['name'],
        "artist": selected_song['artist'],
        "album": selected_song['album'],
        "release_date": selected_song['release_date'],
        "url": f"https://open.spotify.com/track/{selected_song['id']}"
    }

# home route that returns below text when root url is accessed
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/suggestion", methods=["POST"])
def suggestion():
    # converting json object received from the frontend
    text = request.json.get("moodInput", "")

    if not text:
        return jsonify({"error": "Please enter some text."}), 400

    # Remove punctuation and convert to lowercase
    text_cleaned = re.sub(r'[^\w\s]', '', text.lower())
    text_req = [' '.join([word for word in word_tokenize(text_cleaned) if word not in stopwords.words('english')])]

    # Use the same vectorizer and classifier as trained on cleaned data
    prediction = model.predict(vectorizer.transform(text_req))
    song = get_song_by_emotion(emotions[prediction[0]])

    print("Prediction:", prediction[0])
    print("Emotion:", emotions[prediction[0]])
    print("Selected Song:")
    print(song)

    return jsonify({
        "mood": emotions[prediction[0]],
        "song": {
            "name": song["name"],
            "artist": song["artist"],
            "url": song["url"]
        }
    }), 200

if __name__ == '__main__':
   print("Starting Flask app...")
   app.run()