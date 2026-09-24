from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
import pandas as pd

app = Flask(__name__, template_folder=".")

# Load dataset
songs_df = pd.read_csv("songs.csv")

# --- Function to detect emotion ---
def detect_emotion(user_input):
    text = user_input.lower()

    # Keyword-based emotion detection
    if any(word in text for word in ["excited", "energetic", "thrilled", "hyped", "pumped"]):
        return "excited"
    if any(word in text for word in ["happy", "joy", "glad", "cheerful", "delighted", "smiling", "exicted"]):
        return "happy"
    if any(word in text for word in ["sad", "lonely", "upset", "unhappy", "depressed", "crying", "down"]):
        return "sad"
    if any(word in text for word in ["calm", "relaxed", "peace", "chill", "soothing", "serene", "quiet"]):
        return "calm"
    if any(word in text for word in ["angry", "mad", "furious", "rage", "annoyed", "frustrated"]):
        return "angry"
    if any(word in text for word in ["romantic", "love", "heart", "affection", "date", "caring"]):
        return "romantic"
    if any(word in text for word in ["stressed", "tired", "tense", "worried", "anxious", "overwhelmed"]):
        return "stressed"
  

    # Fallback: sentiment analysis with TextBlob
    analysis = TextBlob(user_input)
    polarity = analysis.sentiment.polarity

    if polarity > 0.2:
        return "happy"
    elif polarity < -0.2:
        return "sad"
    else:
        return "calm"


# --- Function to recommend songs for a given emotion ---
def get_songs_for_emotion(emotion):
    filtered = songs_df[songs_df['emotion'] == emotion]
    return filtered.to_dict(orient="records")


# --- Route for home page ---
@app.route("/", methods=["GET", "POST"])
def home():
    emotion = None
    recommendations = []
    if request.method == "POST":
        feeling = request.form["feeling"]
        emotion = detect_emotion(feeling)
        recommendations = get_songs_for_emotion(emotion)
    return render_template("index.html", emotion=emotion, recommendations=recommendations)


# --- Route for about page ---
@app.route("/about")
def about():
    return render_template("about.html")


# --- Route for contact page ---
@app.route("/contact", methods=["GET", "POST"])
def contact():
    message_sent = False
    name = None
    if request.method == "POST":
        # In a real app you'd validate and store/send this message.
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        # For now we simply mark as sent and show a confirmation.
        message_sent = True
    return render_template("contact.html", message_sent=message_sent, name=name)


# --- Route for albums page ---
@app.route("/albums")
def albums():
    return render_template("albums.html", albums=get_albums())


def get_albums():
    # Group songs by artist (treating each artist as an album)
    artists = songs_df['artist'].unique()
    albums_list = []
    for artist in artists:
        artist_songs = songs_df[songs_df['artist'] == artist]
        albums_list.append({
            'artist': artist,
            'song_count': len(artist_songs),
            'songs': artist_songs.to_dict(orient="records")
        })
    return albums_list


@app.route('/albums.json')
def albums_json():
    return jsonify(get_albums())


# --- Route for favorites page ---
@app.route("/favorites")
def favorites():
    return render_template("favorites.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


if __name__ == "__main__":
    # Fix for Windows socket error: disable auto-reloader
    app.run(debug=True, use_reloader=False)