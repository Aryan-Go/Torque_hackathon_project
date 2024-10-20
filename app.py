from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

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

@app.route('/logout_dashboard')
def logout_dashboard():
    return render_template('logout_dashboard.html')  # Render the logout dashboard

@app.route('/logout', methods=['GET'])  # Ensure this route accepts POST requests
@login_required
def logout():
    logout_user()  # Log out the user
    flash('You have been logged out.', 'info')  # Flash a logout message
    return redirect(url_for('logout_dashboard'))  # Redirect to the logout dashboard


# New routes for additional HTML files
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
@login_required  # This ensures that only logged-in users can access this page
def relevancy_meter():
    return render_template('index.html')

@app.route('/exam')
@login_required  # Ensure that only logged-in users can access this page
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
