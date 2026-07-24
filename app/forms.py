from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, Regexp


class RegisterForm(FlaskForm):
    username = StringField(
        "아이디",
        validators=[
            DataRequired(),
            Length(min=4, max=30),
            Regexp(r"^[A-Za-z0-9_]+$", message="영문, 숫자, 밑줄만 사용할 수 있습니다."),
        ],
    )
    password = PasswordField(
        "비밀번호",
        validators=[
            DataRequired(),
            Length(min=8, max=128),
            Regexp(
                r"^(?=.*[A-Za-z])(?=.*\d).+$",
                message="비밀번호는 영문과 숫자를 각각 하나 이상 포함해야 합니다.",
            ),
        ],
    )
    password_confirm = PasswordField(
        "비밀번호 확인",
        validators=[DataRequired(), EqualTo("password", message="비밀번호가 일치하지 않습니다.")],
    )
    submit = SubmitField("회원가입")


class LoginForm(FlaskForm):
    username = StringField("아이디", validators=[DataRequired(), Length(max=30)])
    password = PasswordField("비밀번호", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("로그인")


class ProductForm(FlaskForm):
    title = StringField("상품명", validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField("설명", validators=[DataRequired(), Length(min=2, max=2000)])
    price = IntegerField("가격", validators=[DataRequired(), NumberRange(min=0, max=100_000_000)])
    submit = SubmitField("저장")


class EmptyForm(FlaskForm):
    submit = SubmitField("확인")
