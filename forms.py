from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, SubmitField, RadioField, HiddenField
from wtforms.validators import InputRequired, Length, EqualTo, Email, DataRequired, NumberRange

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(message='Name is required.'),
                                           Length(min=2, max=50, message='Name must be between 2 and 50 characters.')])
    surname = StringField('Surname', validators=[InputRequired(message='Surname is required.'),
                                                 Length(min=2, max=50,
                                                        message='Surname must be between 2 and 50 characters.')])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[
        InputRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[InputRequired(message='Confirm Password is required.'),
                                                 EqualTo('password', message='Passwords do not match.')])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[InputRequired(message='Password is required'),
                                                     Length(min=6,
                                                            message='Password must be at least 6 characters')])

class ExamForm(FlaskForm):
    get_exam = SelectField('Select Exam', choices=[('Python', 'Python'), ('Network', 'Network'), ('Git', 'Git'), ('English', 'English'), ('SQL', 'SQL')])


class UpdateQuestionsCountForm(FlaskForm):
    questions_count = IntegerField('Questions Count', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Send')

class ExamQuestionForm(FlaskForm):
    choice_a = RadioField('Choice A', validators=[DataRequired()])
    choice_b = RadioField('Choice B', validators=[DataRequired()])
    choice_c = RadioField('Choice C', validators=[DataRequired()])
    choice_d = RadioField('Choice D', validators=[DataRequired()])
    selected_choice = HiddenField('Selected Choice', validators=[DataRequired()])

# class ExamQuestionForm(FlaskForm):
#     choice_a = RadioField('Choice A')
#     choice_b = RadioField('Choice B')
#     choice_c = RadioField('Choice C')
#     choice_d = RadioField('Choice D')
