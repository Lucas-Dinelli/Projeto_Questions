from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Admin(db.Model, UserMixin):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    nome = db.Column(db.String, nullable=False)
    senha = db.Column(db.String, nullable=False) # Ver depois como guardar uma senha de forma correta (criptografada)

    def __init__(self, username, nome, senha):
        self.username = username
        self.nome = nome
        self.setSenha(senha)

    def setSenha(self, senha):
        self.senha = generate_password_hash(senha)

    def getVerificacaoDeSenha(self, senha):
        return check_password_hash(self.senha, senha)

    def __repr__(self):
        return '<Admin %r>' % self.username



class Questao(db.Model):
    __tablename__ = "questoes"

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    resposta = db.Column(db.String, nullable=False)
    primeira_opcao_errada = db.Column(db.String, nullable=False)
    segunda_opcao_errada = db.Column(db.String, nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    id_admin = db.Column(db.Integer, db.ForeignKey('admins.id'))

    categoria = db.relationship('Categoria', foreign_keys=id_categoria)
    admin = db.relationship('Admin', foreign_keys=id_admin)

    def __init__(self, texto, resposta, primeiraOpcaoErrada, segundaOpcaoErrada, idCategoria, idAdmin):
        self.texto = texto
        self.resposta = resposta
        self.primeira_opcao_errada = primeiraOpcaoErrada
        self.segunda_opcao_errada = segundaOpcaoErrada
        self.id_categoria = idCategoria
        self.id_admin = idAdmin

    def correcaoDeQuestao(self, opcaoEscolhida):
        if opcaoEscolhida == self.resposta:
            return 1
        else:
            return -1

    def __repr__(self):
        return '<Questao %r>' % self.texto



class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)

    def __init__(self, nome):
        self.nome = nome

    def __repr__(self):
        return '<Categoria %r>' % self.nome



class Player(db.Model, UserMixin):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    senha = db.Column(db.String, nullable=False) # Ver depois como guardar uma senha de forma correta (criptografada)
    pontuacao = db.Column(db.Integer, nullable=False)

    def __init__(self, username, senha, pontuacao):
        self.username = username
        self.setSenha(senha)
        self.setPontuacao(pontuacao)

    def setSenha(self, senha):
        self.senha = generate_password_hash(senha)

    def getVerificacaoDeSenha(self, senha):
        return check_password_hash(self.senha, senha)

    def setPontuacao(self, pontuacao):
        if self.pontuacao != None:
            novaPontuacao = self.pontuacao + pontuacao
            if novaPontuacao >= 0:
                self.pontuacao = novaPontuacao
            else:
                self.pontuacao = 0
        else:
            self.pontuacao = 0

    def __repr__(self):
        return '<Player %r>' % self.username



class Cenario(db.Model):
    __tablename__ = "cenarios"

    id = db.Column(db.Integer, primary_key=True)
    idPlayer = db.Column(db.Integer, db.ForeignKey('players.id'))
    idQuestao = db.Column(db.Integer, db.ForeignKey('questoes.id'))
    resultado = db.Column(db.Integer, nullable=False)

    player = db.relationship('Player', foreign_keys=idPlayer)
    questao = db.relationship('Questao', foreign_keys=idQuestao)

    def __init__(self, idPlayer, idQuestao, resultado):
        self.idPlayer = idPlayer
        self.idQuestao = idQuestao
        self.resultado = resultado

    def __repr__(self):
        return '<Cenario %r>' % self.resultado



class Categorizacao(db.Model):
    __tablename__ = "categorizacoes"

    id = db.Column(db.Integer, primary_key=True)
    id_player = db.Column(db.Integer, db.ForeignKey('players.id'))
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    pontuacao = db.Column(db.Integer, nullable=False)

    player = db.relationship('Player', foreign_keys=id_player)
    categoria = db.relationship('Categoria', foreign_keys=id_categoria)

    def __init__(self, idPlayer, idCategoria, pontuacao):
        self.id_player = idPlayer
        self.id_categoria = idCategoria
        self.setPontuacao(pontuacao)


    def setPontuacao(self, pontuacao):
        if self.pontuacao != None:
            novaPontuacao = self.pontuacao + pontuacao
            if novaPontuacao >= 0:
                self.pontuacao = novaPontuacao
            else:
                self.pontuacao = 0
        else:
            if pontuacao >= 0:
                self.pontuacao = pontuacao
            else:
                self.pontuacao = 0

    def __repr__(self):
        return '<Categorizacao %r>' % self.pontuacao