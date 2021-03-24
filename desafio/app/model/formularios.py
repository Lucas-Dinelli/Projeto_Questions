from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired

class Login(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    senha = PasswordField("senha", validators=[DataRequired()])


class CadastroDeJogador(FlaskForm):
    username = StringField("username", validators=[DataRequired()], render_kw={'autofocus': True})
    senha = PasswordField("senha", validators=[DataRequired()])
    confirmacaoDeSenha = PasswordField("confirmacaoDeSenha", validators=[DataRequired()])


class CadastroDeAdmin(FlaskForm):
    username = StringField("username", validators=[DataRequired()], render_kw={'autofocus': True})
    nome = StringField("nome", validators=[DataRequired()])
    senha = PasswordField("senha", validators=[DataRequired()])
    confirmacaoDeSenha = PasswordField("confirmacaoDeSenha", validators=[DataRequired()])


class CadastroDeQuestao(FlaskForm):
    texto = TextAreaField("texto", validators=[DataRequired()], render_kw={'autofocus': True})
    resposta = TextAreaField("resposta", validators=[DataRequired()])
    primeira_opcao_errada = TextAreaField("primeira_opcao_errada", validators=[DataRequired()])
    segunda_opcao_errada = TextAreaField("segunda_opcao_errada", validators=[DataRequired()])
    categoria = StringField("categoria", validators=[DataRequired()])
