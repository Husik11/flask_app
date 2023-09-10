import json
import os
from datetime import datetime
from random import sample
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, current_user, login_required, logout_user
from .. import subject_json_mapping, login_manager
from ..forms import LoginForm, ExamForm, UpdateQuestionsCountForm, ExamQuestionForm, RegisterForm
from ..models import User, Exam, Subject, Question
from .. import db, app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

# @app.route('/userpage', methods=['GET', 'POST'])
# def userpage():
#     form = ExamForm()
#
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             selected_exam = form.get_exam.data
#             session['selected_exam'] = selected_exam
#             flash(f'Selected exam: {selected_exam}', 'info')
#             return redirect(url_for('userpage'))
#
#     exams = Exam.query.filter_by(student_id=current_user.id).all()
#
# #     return render_template('userpage.html', form=form, exams=exams)
#
# from random import sample

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
                    json_file_path = os.path.join(app.root_path, 'static', 'json', json_file_path)
                    with open(json_file_path, 'r') as f:
                        questions = json.load(f)
                        desired_question_count = 40
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
#             if selected_answers[question.id]:
#                 if choices['correct_choice'] == selected_answers[question.id][0]:
#                     points += 1
#                 question.student_choice = selected_answers[question.id][0]
#             else:
#                 question.student_choice = ''
#
#         exam.grade = points
#         db.session.commit()
#
#         return redirect(url_for('home'))
#
#     return render_template('examPage.html', exam_id=exam_id, questions=exam.questions, form=form, json=json)

# @app.route('/adminPage', methods=['GET', 'POST'])
# def adminPage():
#     exams = Exam.query.all()
#     form = UpdateQuestionsCountForm()
#     students = User.query.all()
#
#     if form.validate_on_submit():
#         selected_exam_name = session.get('selected_exam')
#         if selected_exam_name:
#             subject = Subject.query.filter_by(name=selected_exam_name).first()
#             if subject:
#                 exam = Exam(student_id=current_user.id, subject_id=subject.id,
#                             questions_count=subject.default_questions_count, requested_at=datetime.now())
#                 db.session.add(exam)
#                 db.session.commit()
#
#                 json_file_path = subject_json_mapping.get(subject.name)
#                 if json_file_path:
#                     with open(json_file_path, 'r') as f:
#                         questions = json.load(f)
#                         desired_question_count = exam.questions_count
#                         for question_text, choices in sample(questions.items(), desired_question_count):
#                             choices_json = json.dumps(choices)
#                             correct_choice_str = choices.get('correct_choice')
#
#                             question = Question(exam_id=exam.id, question_text=question_text, choices=choices_json,
#                                                 correct_choice=correct_choice_str)
#                             db.session.add(question)
#                         db.session.commit()
#
#                     flash('Exam with questions has been generated and sent to the user.', 'success')
#                 else:
#                     flash('Invalid exam name. Please try again.', 'danger')
#             else:
#                 flash('Invalid exam name. Please try again.', 'danger')
#         else:
#             flash('No exam selected. Please select an exam first.', 'warning')
#
#     return render_template('adminPage.html', exams=exams, form=form, students=students)

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
