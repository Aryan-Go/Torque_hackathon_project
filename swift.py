from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import speech_recognition as sr
import pyttsx3s
import google.generativeai as genai
import os
import threading
import uvicorn

# Flask setup
app_flask = Flask(__name__)
app_flask.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
app_flask.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app_flask)
login_manager = LoginManager(app_flask)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app_flask.route('/')
def home():
    return render_template('home.html')

# Additional Flask routes go here...
# Include all the routes from your original Flask app

# FastAPI setup
app_fastapi = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Fallback to the first voice

def speak(text):
    engine.say(text)
    engine.runAndWait()

def gemini_ai(query):
    try:
        api_key = os.getenv("AIzaSyBe5A8zLOoiu-WB2kuD4KnwIYDTjG2mFK4")  # Replace with your actual API key
        genai.configure(api_key="AIzaSyBe5A8zLOoiu-WB2kuD4KnwIYDTjG2mFK4")
        
        model = genai.GenerativeModel("gemini-pro", generation_config={"temperature": 0.9, "top_p": 1, "top_k": 1, "max_output_tokens": 2048})
        response = model.generate_content(query)
        
        if response.candidates and response.candidates[0].content.parts:
            text_response = response.candidates[0].content.parts[0].text
            speak(text_response)
            return text_response
        return "No response from AI."
    except Exception as e:
        return f"Error in AI response: {str(e)}"

@app_fastapi.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app_fastapi.post("/command")
async def handle_command(request: Request):
    data = await request.json()
    command = data.get("command")

    if command:
        response_text = gemini_ai(command)
        return JSONResponse(content={"response": response_text})
    return JSONResponse(content={"error": "No command provided"}, status_code=400)

@app_fastapi.get("/listen")
async def listen_command():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    try:
        with microphone as source:
            speak("Calibrating the microphone...")
            recognizer.adjust_for_ambient_noise(source)
            speak("Now speak the next question.")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=50)

        command = recognizer.recognize_google(audio).lower()
        gemini_ai(command)
        return JSONResponse(content={"response": "Command processed"})
    except sr.UnknownValueError:
        return JSONResponse(content={"error": "Could not understand audio"}, status_code=400)
    except sr.RequestError as e:
        return JSONResponse(content={"error": f"Could not request results; {e}"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": f"An unexpected error occurred: {str(e)}"}, status_code=500)

# Run both applications
if __name__ == "__main__":
    import sys

    def run_flask():
        app_flask.run(port=5000)  # Flask runs on port 5000

    threading.Thread(target=run_flask).start()  # Start Flask in a separate thread
    uvicorn.run(app_fastapi, host="0.0.0.0", port=8000)  # FastAPI runs on port 8000
