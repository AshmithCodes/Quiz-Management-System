from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from models import db, User, Quiz, Question, Result
from functools import wraps
import traceback # For debugging

# If using Flask-Login:
# from flask_login import LoginManager, login_user, logout_user, current_user, login_required

# --- App Initialization ---
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# If using Flask-Login:
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login' # Redirect here if login required

# --- Database Setup ---
# Create database tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        print("Database tables created (if they didn't exist).")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        traceback.print_exc() # Print detailed traceback

# --- Decorators for Role-Based Access Control ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        # Optionally load user object here if needed frequently
        # user = User.query.get(session['user_id'])
        # if not user: # Handle case where user ID in session doesn't exist anymore
        #     session.pop('user_id', None)
        #     session.pop('user_role', None)
        #     flash('User not found, please log in again.', 'warning')
        #     return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def professor_required(f):
    @wraps(f)
    @login_required # Ensure user is logged in first
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'professor':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index')) # Or student dashboard?
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    @login_required # Ensure user is logged in first
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'student':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index')) # Or professor dashboard?
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        if session['user_role'] == 'professor':
            return redirect(url_for('professor_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

# -- Authentication Routes --
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')

        # Basic Validation
        if not all([username, email, password, confirm_password, role]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        if role not in ['student', 'professor']:
             flash('Invalid role selected.', 'danger')
             return redirect(url_for('register'))

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.', 'warning')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
             db.session.rollback()
             flash(f'An error occurred during registration: {e}', 'danger')
             print(f"Registration Error: {e}")
             traceback.print_exc()
             return redirect(url_for('register'))

    return render_template('register.html', title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
             flash('Username and password are required.', 'danger')
             return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Store user info in session (Flask's secure session)
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            # Redirect based on role
            if user.role == 'professor':
                return redirect(url_for('professor_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
            # If using Flask-Login: login_user(user) # Handles session management
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', title='Login')

@app.route('/logout')
@login_required # Make sure user is logged in to log out
def logout():
    # If using Flask-Login: logout_user()
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# -- Professor Routes --
@app.route('/professor/dashboard')
@professor_required
def professor_dashboard():
    user_id = session['user_id']
    # Fetch quizzes created by this professor
    quizzes = Quiz.query.filter_by(professor_id=user_id).order_by(Quiz.created_at.desc()).all()
    return render_template('professor_dashboard.html', title='Professor Dashboard', quizzes=quizzes)

@app.route('/professor/quiz/create', methods=['GET', 'POST'])
@professor_required
def create_quiz():
    if request.method == 'POST':
        title = request.form.get('quiz_title')
        if not title:
            flash('Quiz title is required.', 'danger')
            return redirect(url_for('create_quiz'))

        try:
            # Create the Quiz object
            new_quiz = Quiz(title=title, professor_id=session['user_id'])
            db.session.add(new_quiz)
            # Flush to get the new_quiz.id before adding questions
            db.session.flush()

            # Process Questions (assuming dynamic addition via naming convention)
            question_count = 0
            i = 1
            while True:
                q_text = request.form.get(f'q{i}_text')
                if not q_text: # Stop when no more question text is found
                    break

                # Basic validation for the current question
                opt_a = request.form.get(f'q{i}_opt_a')
                opt_b = request.form.get(f'q{i}_opt_b')
                opt_c = request.form.get(f'q{i}_opt_c')
                opt_d = request.form.get(f'q{i}_opt_d')
                correct = request.form.get(f'q{i}_correct')

                if not all([opt_a, opt_b, opt_c, opt_d, correct]):
                    flash(f'All fields are required for Question {i}. Quiz not saved.', 'danger')
                    db.session.rollback() # Rollback the entire transaction
                    return redirect(url_for('create_quiz'))
                if correct not in ['a', 'b', 'c', 'd']:
                     flash(f'Invalid correct option selected for Question {i}. Quiz not saved.', 'danger')
                     db.session.rollback()
                     return redirect(url_for('create_quiz'))

                # Create Question object
                new_question = Question(
                    quiz_id=new_quiz.id,
                    text=q_text,
                    option_a=opt_a,
                    option_b=opt_b,
                    option_c=opt_c,
                    option_d=opt_d,
                    correct_option=correct.lower()
                )
                db.session.add(new_question)
                question_count += 1
                i += 1

            if question_count == 0:
                 flash('A quiz must have at least one question. Quiz not saved.', 'danger')
                 db.session.rollback()
                 return redirect(url_for('create_quiz'))

            # Commit the transaction if all questions are valid
            db.session.commit()
            flash('Quiz created successfully!', 'success')
            return redirect(url_for('professor_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while creating the quiz: {e}', 'danger')
            print(f"Quiz Creation Error: {e}")
            traceback.print_exc()
            return redirect(url_for('create_quiz'))

    return render_template('create_quiz.html', title='Create Quiz')

@app.route('/professor/quiz/<int:quiz_id>/results')
@professor_required
def view_quiz_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # Security check: Ensure the logged-in professor owns this quiz
    if quiz.professor_id != session['user_id']:
        flash('You do not have permission to view results for this quiz.', 'danger')
        return redirect(url_for('professor_dashboard'))

    results = Result.query.filter_by(quiz_id=quiz.id)\
                .join(User, Result.student_id == User.id)\
                .add_columns(User.username, Result.score, Result.total_questions, Result.submitted_at)\
                .order_by(Result.submitted_at.desc())\
                .all()

    return render_template('view_quiz_results.html', title=f'Results for {quiz.title}', quiz=quiz, results=results)


# -- Student Routes --
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    # Fetch all available quizzes
    quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    # Fetch results for the current student
    student_results = Result.query.filter_by(student_id=session['user_id'])\
                        .join(Quiz, Result.quiz_id == Quiz.id)\
                        .add_columns(Quiz.title, Result.score, Result.total_questions, Result.submitted_at, Result.id.label('result_id'))\
                        .order_by(Result.submitted_at.desc())\
                        .all()

    # Create a set of quiz IDs the student has already taken
    taken_quiz_ids = {res.quiz_id for res in Result.query.filter_by(student_id=session['user_id']).all()}

    return render_template('student_dashboard.html', title='Student Dashboard',
                           quizzes=quizzes, results=student_results, taken_quiz_ids=taken_quiz_ids)


@app.route('/student/quiz/<int:quiz_id>/take', methods=['GET', 'POST'])
@student_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions.all() # Get all questions for this quiz

    # Prevent retaking the quiz (basic implementation)
    existing_result = Result.query.filter_by(student_id=session['user_id'], quiz_id=quiz_id).first()
    if existing_result:
         flash('You have already taken this quiz.', 'warning')
         # Optionally redirect to their previous result page
         return redirect(url_for('quiz_results', result_id=existing_result.id))


    if request.method == 'POST':
        score = 0
        total = len(questions)
        student_id = session['user_id']

        try:
            for question in questions:
                submitted_answer = request.form.get(f'question_{question.id}')
                if submitted_answer and submitted_answer.lower() == question.correct_option.lower():
                    score += 1

            # Save the result
            new_result = Result(
                student_id=student_id,
                quiz_id=quiz_id,
                score=score,
                total_questions=total
            )
            db.session.add(new_result)
            db.session.commit()

            flash('Quiz submitted successfully!', 'success')
            return redirect(url_for('quiz_results', result_id=new_result.id)) # Redirect to show result

        except Exception as e:
             db.session.rollback()
             flash(f'An error occurred while submitting the quiz: {e}', 'danger')
             print(f"Quiz Submission Error: {e}")
             traceback.print_exc()
             return redirect(url_for('take_quiz', quiz_id=quiz_id)) # Stay on the quiz page

    # GET request: Show the quiz form
    return render_template('take_quiz.html', title=f'Take Quiz: {quiz.title}', quiz=quiz, questions=questions)

@app.route('/student/quiz/result/<int:result_id>')
@student_required
def quiz_results(result_id):
    result = Result.query.get_or_404(result_id)

    # Security check: Ensure the logged-in student owns this result
    if result.student_id != session['user_id']:
        flash('You do not have permission to view this result.', 'danger')
        return redirect(url_for('student_dashboard'))

    quiz = Quiz.query.get(result.quiz_id) # Get the quiz details
    return render_template('quiz_results.html', title='Quiz Result', result=result, quiz=quiz)


# --- Error Handlers (Optional but Recommended) ---
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404 # Create a templates/404.html

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # Rollback session in case of DB error
    return render_template('500.html'), 500 # Create a templates/500.html


# --- Main Execution ---
if __name__ == '__main__':
    # Consider using waitress or gunicorn for production instead of app.run
    app.run(debug=True) # Enable debug mode for development (auto-reloads, shows errors)