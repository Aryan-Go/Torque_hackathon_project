from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import os
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Setup Jinja2 templates for rendering HTML
templates = Jinja2Templates(directory="templates")

# Safely set the voice to avoid IndexErrors
voices = engine.getProperty('voices')
if len(voices) > 100:
    engine.setProperty('voice', voices[100].id)
else:
    engine.setProperty('voice', voices[0].id)  # Fallback to the first voice if index 100 isn't available

# Function to make the system speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to handle Gemini AI responses
def gemini_ai(query):
    try:
        # Configure the AI using the environment variable for the API key
        api_key = os.getenv("AIzaSyBe5A8zLOoiu-WB2kuD4KnwIYDTjG2mFK4")  # Ensure your API key is set as an environment variable
        genai.configure(api_key="AIzaSyBe5A8zLOoiu-WB2kuD4KnwIYDTjG2mFK4")
        
        model = genai.GenerativeModel("gemini-pro", generation_config={"temperature": 0.9 , "top_p":1 , "top_k":1 , "max_output_tokens":2048})
        response = model.generate_content(query)
        
        if response.candidates and response.candidates[0].content.parts:
            text_response = response.candidates[0].content.parts[0].text
            speak(text_response)
            return text_response  # Return the response text
        return "No response from AI."
    except Exception as e:
        return f"Error in AI response: {str(e)}"

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# FastAPI route to handle commands via POST request
@app.post("/command")
async def handle_command(request: Request):
    data = await request.json()
    command = data.get("command")

    if command:
        response_text = gemini_ai(command)
        print(f"Command processed: {command}")  # Debugging output
        return JSONResponse(content={"response": response_text})  # Return response text as JSON
    return JSONResponse(content={"error": "No command provided"}, status_code=400)

# FastAPI route to listen to a voice command and respond
@app.get("/listen")
async def listen_command():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    try:
        with microphone as source:
            speak("Calibrating the microphone...")
            recognizer.adjust_for_ambient_noise(source) 
            speak("Now speak the next question.")
            print("Listening...")  # Optional: Print to console for debugging
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=50)

        # Use Google Speech API to recognize the voice command
        command = recognizer.recognize_google(audio).lower()
        print(f"Command recognized: {command}")  # Debugging output

        gemini_ai(command)  # Get AI response based on command
        return JSONResponse(content={"response": "Command processed"})
    except sr.UnknownValueError:
        return JSONResponse(content={"error": "Could not understand audio"}, status_code=400)
    except sr.RequestError as e:
        return JSONResponse(content={"error": f"Could not request results; {e}"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": f"An unexpected error occurred: {str(e)}"}, status_code=500)

# Entry point to run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)