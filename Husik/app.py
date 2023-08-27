# import json
# from datetime import datetime
# from flask import Flask, render_template, request, redirect, url_for, flash, session
# from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_migrate import Migrate
# from markupsafe import Markup
# from forms import *
#
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qwerty@localhost:5432/students_db'
# app.config['SECRET_KEY'] = 'Chamberofsecrets'
#
# db = SQLAlchemy(app)
# login_manager = LoginManager()
# login_manager.init_app(app)
#
# migrate = Migrate(app, db)
#
#
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     surname = db.Column(db.String(30))
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(128))
#     role = db.Column(db.String(25), default='user')
#
#     exams = db.relationship('Exam', backref='student', lazy='dynamic')
#
#     def set_password(self, password):
#         self.password = generate_password_hash(password)
#
#     def check_password(self, password):
#         return check_password_hash(self.password, password)
#
#
# class Subject(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text)
#
#     exams = db.relationship('Exam', backref='subject', lazy='dynamic')  # Fix the relationship name
#
#
# class Exam(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Fix the reference to 'user.id'
#     subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
#     grade = db.Column(db.Integer, default=0)
#     questions_count = db.Column(db.Integer, nullable=False)
#     requested_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
#     is_sent = db.Column(db.Boolean, default=False)
#
#     questions = db.relationship('Question', backref='exam', lazy='dynamic')
#
#
# class Question(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
#     question_text = db.Column(db.Text, nullable=False)
#     choices = db.Column(db.JSON)
#     correct_choice = db.Column(db.String(10))
#     student_choice = db.Column(db.String(10), default='')
#
#
# @app.route('/', methods=['GET', 'POST'])
# @app.route('/home', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         pass
#     return render_template('index.html')
#
#
# @app.route('/signUp', methods=['GET', 'POST'])
# def signUp():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         new_user = User(name=form.name.data, surname=form.surname.data, email=form.email.data)
#
#         new_user.set_password(form.password.data)
#         db.session.add(new_user)
#         db.session.commit()
#
#         login_user(new_user)
#
#         return redirect(url_for('userpage'))
#
#     return render_template('signUp.html', form=form)
#
#
# @app.route('/signIn', methods=['GET', 'POST'])
# def signIn():
#     form = LoginForm()
#
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#
#     if form.validate_on_submit():
#         email = form.email.data
#         password = form.password.data
#
#         user = User.query.filter_by(email=email).first()
#
#         if user and user.check_password(password):
#             if user.role == "admin":
#                 login_user(user)
#                 return redirect(url_for('adminPage'))
#             else:
#                 login_user(user)
#                 return redirect(url_for('userpage'))
#         else:
#             flash('Login failed. Please check your email and password.', 'danger')
#
#     session['next'] = request.args.get('next')
#
#     return render_template('signIn.html', form=form)
#
# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out', 'success')
#     return redirect(url_for('home'))
#
# @app.route('/userpage', methods=['GET', 'POST'])
# def userpage():
#     form = ExamForm()
#
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             selected_exam = form.get_exam.data
#             subject = Subject.query.filter_by(name=selected_exam).first()
#
#             if subject:
#                 exam = Exam(student_id=current_user.id, subject_id=subject.id,
#                             questions_count=12, requested_at=datetime.now())
#                 db.session.add(exam)
#                 db.session.commit()
#
#                 with open('python.json', 'r') as f:
#                     questions = json.load(f)
#                     for question_text, choices in questions.items():
#                         choices_json = json.dumps(choices)
#                         correct_choice_str = choices.get('correct_choice')
#
#                         question = Question(exam_id=exam.id, question_text=question_text, choices=choices_json,
#                                             correct_choice=correct_choice_str)
#                         db.session.add(question)
#                     db.session.commit()
#
#                 flash('Your exam has been added. Please wait for the exam link.', 'info')
#                 return redirect(url_for('userpage'))
#             else:
#                 flash('Invalid exam name. Please try again.', 'danger')
#     exams = Exam.query.filter_by(student_id=current_user.id).all()
#
#     return render_template('userpage.html', form=form, exams=exams)
#
#
# @app.route('/adminPage', methods=['GET', 'POST'])
# def adminPage():
#     exams = Exam.query.all()
#     form = UpdateQuestionsCountForm()
#     students = User.query.all()
#     if form.validate_on_submit():
#         exam_id = request.form.get('exam_id')
#         new_questions_count = form.questions_count.data
#
#         exam = Exam.query.get(exam_id)
#         if exam:
#             if new_questions_count != exam.questions_count:
#                 exam.questions_count = new_questions_count
#             exam.is_sent = True
#             db.session.commit()
#
#     return render_template('adminPage.html', exams=exams, form=form, students=students)
#
#
# @app.route('/examPage/<int:exam_id>', methods=['POST', 'GET'])
# def examPage(exam_id):
#     exam = Exam.query.get_or_404(exam_id)
#     form = ExamQuestionForm()
#
#     if request.method == 'POST':
#         selected_answers = {}
#         for question in exam.questions:
#             selected_answers[question.id] = request.form.getlist(f'answer{question.id}')
#
#         points = 0
#         for i, question in enumerate(exam.questions):
#             choices = json.loads(question.choices)
#             if choices['correct_choice'] == selected_answers[question.id][0]:
#                 points += 1
#             question.student_choice = selected_answers[question.id][0]
#
#         exam.grade = points
#         db.session.commit()
#
#         return redirect(url_for('home'))
#
#     return render_template('examPage.html', exam_id=exam_id, questions=exam.questions, form=form, json=json)
#
#
#
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)

import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from forms import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qwerty@localhost:5432/students_db'
app.config['SECRET_KEY'] = 'Chamberofsecrets'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

migrate = Migrate(app, db)

subject_json_mapping = {
    'Python': 'python.json',
    'Network': 'network.json',
    'Git': 'git.json',
    'English': 'english.json',
    'SQL': 'sql.json'
}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Fix the reference to 'user.id'
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


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        pass
    return render_template('index.html')


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(name=form.name.data, surname=form.surname.data, email=form.email.data)

        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for('userpage'))

    return render_template('signUp.html', form=form)


@app.route('/signIn', methods=['GET', 'POST'])
def signIn():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if user.role == "admin":
                login_user(user)
                return redirect(url_for('adminPage'))
            else:
                login_user(user)
                return redirect(url_for('userpage'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')

    session['next'] = request.args.get('next')

    return render_template('signIn.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

# import random
#
# @app.route('/userpage', methods=['GET', 'POST'])
# def userpage():
#     form = ExamForm()
#     exams = Exam.query.all()
#
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             selected_exam = form.get_exam.data
#             subject = Subject.query.filter_by(name=selected_exam).first()
#
#             if subject:
#                 exam = Exam(student_id=current_user.id, subject_id=subject.id,
#                             requested_at=datetime.now())
#                 db.session.add(exam)
#                 db.session.commit()
#
#                 json_file_path = subject_json_mapping.get(subject.name)
#                 if json_file_path:
#                     with open(json_file_path, 'r') as f:
#                         questions = json.load(f)
#                         for exam in exams:  # Iterate through each exam
#                             for question_text, choices in random.sample(questions.items(), exam.questions_count):
#                                 choices_json = json.dumps(choices)
#                                 correct_choice_str = choices.get('correct_choice')
#
#                                 question = Question(exam_id=exam.id, question_text=question_text, choices=choices_json,
#                                                     correct_choice=correct_choice_str)
#                                 db.session.add(question)
#                         db.session.commit()
#
#                     flash('Your exam has been added. Please wait for the exam link.', 'info')
#                     return redirect(url_for('userpage'))
#                 else:
#                     flash('Invalid exam name. Please try again.', 'danger')
#             else:
#                 flash('Invalid exam name. Please try again.', 'danger')
#     exams = Exam.query.filter_by(student_id=current_user.id).all()
#     return render_template('userpage.html', form=form, exams=exams)

from random import sample


@app.route('/userpage', methods=['GET', 'POST'])
def userpage():
    form = ExamForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            selected_exam = form.get_exam.data
            subject = Subject.query.filter_by(name=selected_exam).first()

            if subject:
                exam = Exam(student_id=current_user.id, subject_id=subject.id,
                            requested_at=datetime.now())
                db.session.add(exam)
                db.session.commit()

                json_file_path = subject_json_mapping.get(subject.name)
                if json_file_path:
                    with open(json_file_path, 'r') as f:
                        questions = json.load(f)
                        desired_question_count = 25
                        for question_text, choices in sample(questions.items(), desired_question_count):
                            choices_json = json.dumps(choices)
                            correct_choice_str = choices.get('correct_choice')

                            question = Question(exam_id=exam.id, question_text=question_text, choices=choices_json,
                                                correct_choice=correct_choice_str)
                            db.session.add(question)
                        db.session.commit()

                    flash('Your exam has been added. Please wait for the exam link.', 'info')
                    return redirect(url_for('userpage'))
                else:
                    flash('Invalid exam name. Please try again.', 'danger')
            else:
                flash('Invalid exam name. Please try again.', 'danger')

    exams = Exam.query.filter_by(student_id=current_user.id).all()

    return render_template('userpage.html', form=form, exams=exams)


# from random import sample
#
# @app.route('/userpage', methods=['GET', 'POST'])
# def userpage():
#     form = ExamForm()
#
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             selected_exam = form.get_exam.data
#             subject = Subject.query.filter_by(name=selected_exam).first()
#
#             if subject:
#                 exam = Exam(student_id=current_user.id, subject_id=subject.id,
#                             requested_at=datetime.now())
#                 db.session.add(exam)
#                 db.session.commit()
#
#                 json_file_path = subject_json_mapping.get(subject.name)
#                 if json_file_path:
#                     with open(json_file_path, 'r') as f:
#                         questions = json.load(f)
#                         for question_text, choices in sample(questions.items(), exam.questions_count):
#                             choices_json = json.dumps(choices)
#                             correct_choice_str = choices.get('correct_choice')
#
#                             question = Question(exam_id=exam.id, question_text=question_text, choices=choices_json,
#                                                 correct_choice=correct_choice_str)
#                             db.session.add(question)
#                         db.session.commit()
#
#                     flash('Your exam has been added. Please wait for the exam link.', 'info')
#                     return redirect(url_for('userpage'))
#                 else:
#                     flash('Invalid exam name. Please try again.', 'danger')
#             else:
#                 flash('Invalid exam name. Please try again.', 'danger')
#
#     exams = Exam.query.filter_by(student_id=current_user.id).all()
#
#     return render_template('userpage.html', form=form, exams=exams)


# @app.route('/userpage', methods=['GET', 'POST'])
# def userpage():
#     form = ExamForm()
#
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             selected_exam = form.get_exam.data
#             subject = Subject.query.filter_by(name=selected_exam).first()
#
#             if subject:
#                 exam = Exam(student_id=current_user.id, subject_id=subject.id,
#                             questions_count=40, requested_at=datetime.now())
#                 db.session.add(exam)
#                 db.session.commit()
#
#                 json_file_path = subject_json_mapping.get(subject.name)
#                 if json_file_path:
#                     with open(json_file_path, 'r') as f:
#                         questions = json.load(f)
#                         for question_text, choices in questions.items():
#                             choices_json = json.dumps(choices)
#                             correct_choice_str = choices.get('correct_choice')
#
#                             question = Question(exam_id=exam.id, question_text=question_text, choices=choices_json,
#                                                 correct_choice=correct_choice_str)
#                             db.session.add(question)
#                         db.session.commit()
#
#                     flash('Your exam has been added. Please wait for the exam link.', 'info')
#                     return redirect(url_for('userpage'))
#                 else:
#                     flash('Invalid exam name. Please try again.', 'danger')
#             else:
#                 flash('Invalid exam name. Please try again.', 'danger')
#     exams = Exam.query.filter_by(student_id=current_user.id).all()
#
#     return render_template('userpage.html', form=form, exams=exams)

@app.route('/adminPage', methods=['GET', 'POST'])
def adminPage():
    exams = Exam.query.all()
    form = UpdateQuestionsCountForm()
    students = User.query.all()

    if form.validate_on_submit():
        exam_id = request.form.get('exam_id')
        new_questions_count = form.questions_count.data

        if new_questions_count is not None:
            exam = Exam.query.get(exam_id)
            if exam:
                if new_questions_count != exam.questions_count:
                    exam.questions_count = new_questions_count
                exam.is_sent = True
                db.session.commit()
            flash('Questions count has been updated.', 'success')
        else:
            flash('No changes made to questions count.', 'info')

    return render_template('adminPage.html', exams=exams, form=form, students=students)

@app.route('/examPage/<int:exam_id>', methods=['POST', 'GET'])
def examPage(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    form = ExamQuestionForm()

    if request.method == 'POST':
        selected_answers = {}
        for question in exam.questions:
            selected_answers[question.id] = request.form.getlist(f'answer{question.id}')

        points = 0
        for i, question in enumerate(exam.questions):
            choices = json.loads(question.choices)
            if selected_answers[question.id]:
                if choices['correct_choice'] == selected_answers[question.id][0]:
                    points += 1
                question.student_choice = selected_answers[question.id][0]
            else:
                question.student_choice = ''

        exam.grade = points
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('examPage.html', exam_id=exam_id, questions=exam.questions, form=form, json=json)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
