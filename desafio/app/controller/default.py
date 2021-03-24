import flask_login

from app import app, db, login_manager
from flask import render_template, flash, redirect, url_for, request
from app.model.formularios import Login, CadastroDeJogador, CadastroDeAdmin, CadastroDeQuestao
from app.model.tables import Player, Questao, Categoria, Categorizacao, Admin
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user

from random import shuffle


tipoDeUsuario = ""


def indicarTipoDePortalDoUsuarioAtual(localParaRedirecionar):
    if tipoDeUsuario == "player":
        return "portal_jogador"
    elif tipoDeUsuario == "admin":
        return "portal_admin"
    elif localParaRedirecionar == "login_jogador" or localParaRedirecionar == "login_admin":
        return localParaRedirecionar


@login_manager.user_loader
def load_user(usuario_id):
    if tipoDeUsuario == "player":
        return Player.query.filter_by(id=usuario_id).first()
    elif tipoDeUsuario == "admin":
        return Admin.query.filter_by(id=usuario_id).first()


@app.route("/index")
@app.route("/")
def index():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("")))
    return render_template("index.html")


#   <-----------------------------  Parte Jogador   ------------------------------->

@app.route("/cadastro_de_jogador", methods=["POST", "GET"])
def cadastro_de_jogador():
    formulario = CadastroDeJogador()
    resultado = 0
    if not flask_login.current_user.is_authenticated:
        if formulario.validate_on_submit():
            if formulario.senha.data == formulario.confirmacaoDeSenha.data:
                try:
                    novoJogador = Player(formulario.username.data, formulario.senha.data, 0)
                    db.session.add(novoJogador)
                    db.session.commit()
                    resultado = 1
                except IntegrityError:
                    db.session.rollback()
                    resultado = 2
                    pass
            else:
                resultado = 3
    else:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("")))
    return render_template("cadastro_de_jogador.html", formulario=formulario, resultado=resultado)


@app.route("/login_jogador/<username>", methods=["POST", "GET"])
@app.route("/login_jogador", defaults={"username": ""}, methods=["POST", "GET"])
def login_jogador(username):
    formulario = Login()
    if flask_login.current_user.is_authenticated:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("")))
    elif formulario.validate_on_submit():
        jogador = Player.query.filter_by(username=formulario.username.data).first()
        if jogador and jogador.getVerificacaoDeSenha(formulario.senha.data):
            global tipoDeUsuario
            tipoDeUsuario = "player"
            login_user(jogador)
            return redirect(url_for("portal_jogador"))
        else:
            flash("Login e/ou senha incorretos!")
    return render_template("login.html", formulario=formulario, username=username)


@app.route("/portal_jogador")
def portal_jogador():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("login_jogador")))
    elif tipoDeUsuario != "player":
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("")))
    return render_template("portal_jogador.html")


@app.route("/portal_jogador_editar_perfil", methods=["POST", "GET"])
def portal_jogador_editar_perfil():
    formulario = CadastroDeJogador()
    jogador = flask_login.current_user
    username = None
    resultado = 0
    if jogador.is_authenticated and tipoDeUsuario == "player":
        if formulario.validate_on_submit():
            username = formulario.username.data
            if formulario.senha.data == formulario.confirmacaoDeSenha.data:
                try:
                    jogador.username = username
                    jogador.setSenha(formulario.senha.data)
                    db.session.commit()
                    resultado = 1
                except IntegrityError:
                    db.session.rollback()
                    resultado = 2
                    pass
            else:
                resultado = 3
        if formulario.senha.data and jogador.getVerificacaoDeSenha(formulario.senha.data):
            username = jogador.username
        elif formulario.senha.data:
            resultado = 3
    else:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("login_jogador")))

    return render_template("portal_jogador_editar_perfil.html", formulario=formulario, username=username, resultado=resultado)


@app.route("/portal_jogador_ranking/<id_categoria>")
@app.route("/portal_jogador_ranking/", defaults={"id_categoria": None})
def portal_jogador_ranking(id_categoria):
    jogador = flask_login.current_user
    if jogador.is_authenticated and tipoDeUsuario == "player":
        listaDeJogadores = Player.query.order_by(Player.pontuacao).all()
        listaDeCategorias = Categoria.query.order_by(Categoria.nome).all()
        listaDeResultados = []
        if id_categoria != None:
            results = Categorizacao.query.filter_by(id_categoria=id_categoria).join(Player, Categorizacao.id_player==Player.id).add_columns(Player.username, Categorizacao.pontuacao).order_by(Categorizacao.pontuacao)
            for r in results:
                listaDeResultados.append((r[1], r[2]))

            listaDeResultados.append(Categoria.query.filter_by(id=id_categoria).first().nome)
    else:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("login_jogador")))

    return render_template("portal_jogador_ranking.html", listaDeJogadores=listaDeJogadores, listaDeCategorias=listaDeCategorias, id_categoria=id_categoria, listaDeResultados=listaDeResultados)


@app.route("/questionario/<id_categoria>", methods=["POST", "GET"])
@app.route("/questionario", defaults={"id_categoria": None})
def questionario(id_categoria):
    #listaDeCategorias = []
    global listaDeQuestoes
    numeroMinimoDeQuestoes = 10
    isACategoryWithoutEnoughQuestion = False
    global listaDeAlternativas
    resultado = 1
    if flask_login.current_user.is_authenticated and tipoDeUsuario == "player":
        listaDeCategorias = Categoria.query.order_by(Categoria.nome).all()
        if request.method == 'POST':
            resultado = 2
            pontuacao = 0
            for i in range(numeroMinimoDeQuestoes):
                if len(request.form.getlist("flexRadioDefault" + str(i))) == 0:
                    # Caso a questão (i) não tenha sido respondida...
                    resultado = 3
                    flash("Por favor, preencha todas as questões!", "danger")
                    break
                else:
                    opcaoEscolhida = request.form.getlist("flexRadioDefault" + str(i))[0]
                    pontuacao = pontuacao + listaDeQuestoes[i].correcaoDeQuestao(opcaoEscolhida)
                    if i == numeroMinimoDeQuestoes-1:
                        jogador = flask_login.current_user
                        jogador.setPontuacao(pontuacao)
                        db.session.commit()
                        categorizacao = list(Categorizacao.query.filter_by(id_player=jogador.id, id_categoria=id_categoria))
                        if categorizacao:
                            categorizacao[0].setPontuacao(pontuacao)
                            db.session.commit()
                        else:
                            db.session.add(Categorizacao(jogador.id, id_categoria, pontuacao))
                            db.session.commit()
                        flash("Sua pontuação neste questionário foi de " + str(pontuacao) + " ponto(s).", "info")
        elif id_categoria:
            listaDeQuestoes = list(Questao.query.filter_by(id_categoria=id_categoria))
            if len(listaDeQuestoes) < numeroMinimoDeQuestoes:
                isACategoryWithoutEnoughQuestion = True
            else:
                shuffle(listaDeQuestoes)
                listaDeAlternativas.clear()
                for questao in listaDeQuestoes:
                    alternativas = [questao.resposta, questao.primeira_opcao_errada, questao.segunda_opcao_errada]
                    shuffle(alternativas)
                    listaDeAlternativas.append(alternativas)
        else:
            listaDeQuestoes = []
            listaDeAlternativas = []
    else:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("login_jogador")))
    return render_template("questionario.html", listaDeCategorias=listaDeCategorias, listaDeQuestoes=listaDeQuestoes, numeroMinimoDeQuestoes=numeroMinimoDeQuestoes, isACategoryWithoutEnoughQuestion=isACategoryWithoutEnoughQuestion, listaDeAlternativas=listaDeAlternativas, resultado=resultado)


#   <--------------------------------------------------------------------------------->


@app.route("/logout")
def logout():
    global tipoDeUsuario
    tipoDeUsuario = ""
    logout_user()
    return redirect(url_for("index"))


# <-----------------------------  Parte Administrador   ------------------------------->


@app.route("/cadastro_de_admin", methods=["POST", "GET"])
def cadastro_de_admin():
    formulario = CadastroDeAdmin()
    resultado = 0
    if flask_login.current_user.is_authenticated and tipoDeUsuario == "admin":
        if formulario.validate_on_submit():
            if formulario.senha.data == formulario.confirmacaoDeSenha.data:
                try:
                    novoAdmin = Admin(formulario.username.data, formulario.nome.data, formulario.senha.data)
                    db.session.add(novoAdmin)
                    db.session.commit()
                    resultado = 1
                except IntegrityError:
                    db.session.rollback()
                    resultado = 2
                    pass
            else:
                resultado = 3
    else:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("login_admin")))
    return render_template("cadastro_de_admin.html", formulario=formulario, resultado=resultado)



@app.route("/login_admin", methods=["POST", "GET"])
def login_admin():
    formulario = Login()
    if flask_login.current_user.is_authenticated:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("")))
    elif formulario.validate_on_submit():
        admin = Admin.query.filter_by(username=formulario.username.data).first()
        if admin and admin.getVerificacaoDeSenha(formulario.senha.data):
            global tipoDeUsuario
            tipoDeUsuario = "admin"
            login_user(admin)
            return redirect(url_for("portal_admin"))
        else:
            flash("Login e/ou senha incorretos!")
        ...
        #Admin

    return render_template("login_admin.html", formulario=formulario, username="")


@app.route("/portal_admin")
def portal_admin():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("login_admin")))
    elif tipoDeUsuario != "admin":
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("")))
    return render_template("portal_admin.html")


@app.route("/portal_admin_editar_perfil", methods=["POST", "GET"])
def portal_admin_editar_perfil():
    formulario = CadastroDeAdmin()
    admin = flask_login.current_user
    username = None
    resultado = 0
    if admin.is_authenticated and tipoDeUsuario == "admin":
        if formulario.validate_on_submit():
            print("OK")
            username = formulario.username.data
            if formulario.senha.data == formulario.confirmacaoDeSenha.data:
                try:
                    admin.username = username
                    admin.nome = formulario.nome.data
                    admin.setSenha(formulario.senha.data)
                    db.session.commit()
                    resultado = 1
                except IntegrityError:
                    db.session.rollback()
                    resultado = 2
                    pass
            else:
                resultado = 3
        if formulario.senha.data and admin.getVerificacaoDeSenha(formulario.senha.data):
            username = admin.username
        elif formulario.senha.data:
            resultado = 3
    else:
        return redirect(url_for(indicarTipoDePortalDoUsuarioAtual("login_jogador")))
    return render_template("portal_admin_editar_perfil.html", formulario=formulario, username=username, resultado=resultado)


@app.route("/cadastro_de_questao", methods=["POST", "GET"])
def cadastro_de_questao():
    formulario = CadastroDeQuestao()
    listaDeCategorias = Categoria.query.order_by(Categoria.nome).all()
    if flask_login.current_user.is_authenticated and tipoDeUsuario == "admin":
        if formulario.validate_on_submit():
            categoria = Categoria.query.filter_by(nome=formulario.categoria.data).first()
            if not categoria:
                novaCategoria = Categoria(formulario.categoria.data)
                db.session.add(novaCategoria)
                db.session.commit()
                categoria = novaCategoria
            novaQuestao = Questao(formulario.texto.data, formulario.resposta.data,
                                  formulario.primeira_opcao_errada.data, formulario.segunda_opcao_errada.data,
                                  categoria.id, flask_login.current_user.id)
            db.session.add(novaQuestao)
            db.session.commit()
            flash("Questão adicionada com sucesso!")
    return render_template("cadastro_de_questao.html", formulario=formulario, listaDeCategorias=listaDeCategorias)

#   <------------------------------------------------------------------------------->
