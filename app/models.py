from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_manager
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(30))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String(25), default='user')

    exams = db.relationship('Exam', backref='student', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    exams = db.relationship('Exam', backref='subject', lazy='dynamic')


class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade = db.Column(db.Integer, default=0)
    questions_count = db.Column(db.Integer, nullable=False, default=20)
    requested_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    is_sent = db.Column(db.Boolean, default=False)

    questions = db.relationship('Question', backref='exam', lazy='dynamic')


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    choices = db.Column(db.JSON)
    correct_choice = db.Column(db.String(10))
    student_choice = db.Column(db.String(10), default='')
