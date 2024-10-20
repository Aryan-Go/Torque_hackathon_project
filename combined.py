from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # You can change this as needed
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize text-to-speech engine
engine = pyttsx3.init()

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
        api_key = os.getenv("AIzaSyBe5A8zLOoiu-WB2kuD4KnwIYDTjG2mFK4")  # Ensure your API key is set as an environment variable
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel("gemini-pro", generation_config={"temperature": 0.9, "top_p": 1, "top_k": 1, "max_output_tokens": 2048})
        response = model.generate_content(query)
        
        if response.candidates and response.candidates[0].content.parts:
            text_response = response.candidates[0].content.parts[0].text
            speak(text_response)
            return text_response  # Return the response text
        return "No response from AI."
    except Exception as e:
        return f"Error in AI response: {str(e)}"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        # Check if username or email already exists
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Username or Email already exists.', 'danger')
            return redirect(url_for('signup'))
        
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Check your email and password', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()  # Log out the user
    flash('You have been logged out.', 'info')  # Flash a logout message
    return redirect(url_for('home'))

@app.route('/command', methods=['POST'])
@login_required
def handle_command():
    data = request.json
    command = data.get("command")

    if command:
        response_text = gemini_ai(command)
        print(f"Command processed: {command}")  # Debugging output
        return jsonify({"response": response_text})
    return jsonify({"error": "No command provided"}), 400

@app.route('/listen', methods=['GET'])
@login_required
def listen_command():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    try:
        with microphone as source:
            speak("Calibrating the microphone...")
            recognizer.adjust_for_ambient_noise(source) 
            speak("Now speak the next question.")
            print("Listening...")  # Optional: Print to console for debugging
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=50)

        command = recognizer.recognize_google(audio).lower()
        print(f"Command recognized: {command}")  # Debugging output

        response_text = gemini_ai(command)  # Get AI response based on command
        return jsonify({"response": response_text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Could not request results; {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Additional routes for your HTML files
@app.route('/physics_chap')
@login_required
def physics_chap():
    return render_template('physics_chap.html')

@app.route('/physics_book')
@login_required
def physics_book():
    return render_template('physics_book.html')

@app.route('/mathematics_chap')
@login_required
def mathematics_chap():
    return render_template('mathematics_chap.html')

@app.route('/mathematics_book')
@login_required
def mathematics_book():
    return render_template('mathematics_book.html')

@app.route('/leaderboard')
@login_required
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/jee_prep')
@login_required
def jee_prep():
    return render_template('jee_prep.html')

@app.route('/important_chap')
@login_required
def important_chap():
    return render_template('important_chap.html')

@app.route('/important_book')
@login_required
def important_book():
    return render_template('important_book.html')

@app.route('/chemistry_chap')
@login_required
def chemistry_chap():
    return render_template('chemistry_chap.html')

@app.route('/timer')
@login_required
def timer():
    return render_template('timer.html')

@app.route('/chemistry_book')
@login_required
def chemistry_book():
    return render_template('chemistry_book.html')

@app.route('/relevancy_meter')
@login_required
def relevancy_meter():
    return render_template('index.html')

@app.route('/exam')
@login_required
def exam():
    return render_template('exam.html')

# Route for about.html
@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/phy_q1')
def phy_q1():
    return render_template('phy_q1.html')

@app.route('/phy_q2')
def phy_q2():
    return render_template('phy_q2.html')

@app.route('/phy_q3')
def phy_q3():
    return render_template('phy_q3.html')

@app.route('/phy_q4')
def phy_q4():
    return render_template('phy_q4.html')

@app.route('/phy_q5')
def phy_q5():
    return render_template('phy_q5.html')

@app.route('/phy_q6')
def phy_q6():
    return render_template('phy_q6.html')

@app.route('/phy_q7')
def phy_q7():
    return render_template('phy_q7.html')

@app.route('/phy_q8')
def phy_q8():
    return render_template('phy_q8.html')

@app.route('/phy_q9')
def phy_q9():
    return render_template('phy_q9.html')

@app.route('/phy_q10')
def phy_q10():
    return render_template('phy_q10.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates database tables
    app.run(debug=True)
