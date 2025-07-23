Online Quiz Management System

A Flask-based web application that allows professors to create and manage quizzes while students can take quizzes and view their results. The system features role-based access control, secure authentication, and a database-backed architecture for managing users, quizzes, and results.
Features
✅ User Authentication & Roles

    Registration and login with secure password hashing.

    Two user roles: Professor and Student.

    Role-based access control using custom decorators.

✅ Professor Dashboard

    Create quizzes with multiple-choice questions.

    View results submitted by students.

    Manage quizzes (view and monitor performance).

✅ Student Dashboard

    View available quizzes.

    Take quizzes only once per quiz.

    View past results after submission.

✅ Result Management

    Automatic scoring based on correct answers.

    Professors can view all student submissions for their quizzes.

    Students can track their performance.

✅ Error Handling

    Flash messages for feedback and form validation.

    Custom 404 and 500 error pages.

Technology Stack
Component	Technology
Backend	Python (Flask Framework)
Database	SQLite (default), SQLAlchemy ORM
Frontend	Flask Jinja2 Templates (HTML, CSS, Bootstrap recommended)
Security	Werkzeug for password hashing, Flask sessions
Other	Role-based decorators for access control
Installation & Setup
1. Clone the Repository

git clone https://github.com/your-username/online-quiz-system.git
cd online-quiz-system

2. Create Virtual Environment & Install Dependencies

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt

(If you don’t have requirements.txt, you can generate one using: pip freeze > requirements.txt)
3. Configure Environment Variables (Optional)

Edit config.py if you want to change database or secret key:

SECRET_KEY = 'change-this-in-production'
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'  # Or PostgreSQL/MySQL URI

4. Initialize the Database

python
>>> from app1 import db
>>> db.create_all()

Or simply run the app once; it will auto-create tables.
5. Run the Application

python app1.py

Visit http://127.0.0.1:5000/ in your browser.
Project Structure

|-- app1.py             # Main Flask application (routes & logic)
|-- config.py           # App configuration (DB, secret key)
|-- models.py           # Database models (User, Quiz, Question, Result)
|-- app.db              # SQLite database (auto-created)
|-- templates/          # HTML templates (Jinja2)
|   |-- register.html
|   |-- login.html
|   |-- professor_dashboard.html
|   |-- student_dashboard.html
|   |-- take_quiz.html
|   |-- quiz_results.html
|   |-- 404.html / 500.html
|-- static/             # (Optional) CSS, JS, images
|-- requirements.txt    # Python dependencies

Usage Guide
Professor Workflow

   * Register as a professor.

   * Log in and access the Professor Dashboard.

   * Create quizzes with multiple-choice questions.

   * View students’ results for each quiz.

Student Workflow

   * Register as a student.

   * Log in and access the Student Dashboard.

   * Take available quizzes (only once per quiz).

   * View quiz results after submission.

Future Enhancements

   * Timer-based quizzes and question randomization.

   * Leaderboards and analytics for performance tracking.

   * Email notifications for quiz availability and results.

   * Migration to Flask-Login for better session management.

License

This project is open-source. You can use and modify it freely.