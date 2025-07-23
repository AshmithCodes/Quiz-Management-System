from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# If using Flask-Login: from flask_login import UserMixin

db = SQLAlchemy()

# If using Flask-Login, add UserMixin: class User(UserMixin, db.Model):
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256)) # Increased length for stronger hashes
    role = db.Column(db.String(10), nullable=False) # 'student' or 'professor'

    # Relationships
    quizzes_created = db.relationship('Quiz', foreign_keys='Quiz.professor_id', backref='creator', lazy='dynamic')
    results = db.relationship('Result', foreign_keys='Result.student_id', backref='student', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

    # Required properties for Flask-Login if used
    @property
    def is_active(self): return True
    @property
    def is_authenticated(self): return True
    @property
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade="all, delete-orphan")
    results = db.relationship('Result', backref='quiz', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Quiz {self.title}>'


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False) # 'a', 'b', 'c', or 'd'

    def __repr__(self):
        return f'<Question {self.id} for Quiz {self.quiz_id}>'


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Result by Student {self.student_id} for Quiz {self.quiz_id} - Score: {self.score}/{self.total_questions}>'

# If using Flask-Login, add this function:
# login_manager = LoginManager()
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))