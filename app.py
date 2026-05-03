from flask import Flask, render_template, request, redirect, url_for, session
from bson import ObjectId
from datetime import datetime
import calendar

from conexao import conectar, obter_db
from transacoes import inserir_transacao, buscar_transacoes_por_usuario, deletar_transacao
from relatorios import relatorio_dashboard
from usuarios import buscar_usuario_por_email, inserir_usuario
from contas import buscar_contas_por_usuario, inserir_conta
from categorias import buscar_todas_categorias, buscar_categoria_por_nome, inserir_categorias_padrao

app = Flask(__name__)
app.secret_key = "financas_nosql_chave_secreta"

conectar()
db = obter_db()


def usuario_logado():
    return "usuario_id" in session


@app.route("/")
def index():
    if not usuario_logado():
        return redirect(url_for("login"))

    usuario_id = ObjectId(session["usuario_id"])
    hoje = datetime.now()
    mes_sel = int(request.args.get("mes", hoje.month))
    ano_sel = int(request.args.get("ano", hoje.year))

    ultimo_dia = calendar.monthrange(ano_sel, mes_sel)[1]
    data_limite = datetime(ano_sel, mes_sel, ultimo_dia, 23, 59, 59)

    contas_brutas = buscar_contas_por_usuario(usuario_id)
    contas_finais = []

    for conta in contas_brutas:
        pipeline = [
            {"$match": {
                "conta_id": conta["_id"],
                "data": {"$lte": data_limite}
            }},
            {"$group": {
                "_id": None,
                "saldo": {
                    "$sum": {
                        "$cond": [{"$eq": ["$tipo", "entrada"]}, "$valor", {"$multiply": ["$valor", -1]}]
                    }
                }
            }}
        ]
        res = list(db.transacoes.aggregate(pipeline))
        conta["saldo_exibicao"] = res[0]["saldo"] if res else 0.0
        contas_finais.append(conta)

    return render_template(
        "index.html",
        usuario_nome=session["usuario_nome"],
        usuario_id=session["usuario_id"],
        contas=contas_finais,
        transacoes=buscar_transacoes_por_usuario(usuario_id),
        dashboard=relatorio_dashboard(usuario_id, mes_sel, ano_sel),
        categorias=buscar_todas_categorias(),
        mes=mes_sel,
        ano=ano_sel
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if usuario_logado():
        return redirect(url_for("index"))

    erro = None
    if request.method == "POST":
        email = request.form.get("email").strip()
        senha = request.form.get("senha")

        usuario = buscar_usuario_por_email(email)

        if usuario and usuario.get("senha") == senha:
            session["usuario_id"] = str(usuario["_id"])
            session["usuario_nome"] = usuario["nome"]
            return redirect(url_for("index"))
        else:
            erro = "E-mail ou senha incorretos."

    return render_template("login.html", erro=erro)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if usuario_logado():
        return redirect(url_for("index"))

    erro = None
    if request.method == "POST":
        nome = request.form.get("nome").strip()
        email = request.form.get("email").strip()
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar")

        if senha != confirmar:
            erro = "As senhas não coincidem."
        elif buscar_usuario_por_email(email):
            erro = "Este e-mail já está cadastrado."
        else:
            uid = inserir_usuario(nome, email, senha)

            if db.categorias.count_documents({}) == 0:
                inserir_categorias_padrao()

            inserir_conta(uid, "Conta Principal", "corrente")

            session["usuario_id"] = str(uid)
            session["usuario_nome"] = nome
            return redirect(url_for("index"))

    return render_template("cadastro.html", erro=erro)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/add_transacao", methods=["POST"])
def add_transacao():
    if not usuario_logado():
        return redirect(url_for("login"))

    usuario_id = ObjectId(session["usuario_id"])
    conta_id = ObjectId(request.form.get("conta_id"))
    valor = float(request.form.get("valor"))
    tipo = request.form.get("tipo")
    descricao = request.form.get("descricao")
    categoria_nome = request.form.get("categoria")

    data_str = request.form.get("data")
    data_dt = datetime.strptime(data_str, "%Y-%m-%d") if data_str else datetime.now()

    cat_obj = buscar_categoria_por_nome(categoria_nome)
    icone = cat_obj["icone"] if cat_obj else "💰"

    inserir_transacao(usuario_id, conta_id, valor, tipo, descricao, categoria_nome, icone, data_dt)
    return redirect(url_for("index"))


@app.route("/editar_transacao", methods=["POST"])
def editar_transacao():
    if not usuario_logado():
        return redirect(url_for("login"))

    transacao_id = ObjectId(request.form.get("transacao_id"))
    data_str = request.form.get("data")
    data_dt = datetime.strptime(data_str, "%Y-%m-%d")

    db.transacoes.update_one(
        {"_id": transacao_id},
        {"$set": {
            "descricao": request.form.get("descricao"),
            "valor": float(request.form.get("valor")),
            "tipo": request.form.get("tipo"),
            "data": data_dt,
            "categoria.nome": request.form.get("categoria"),
        }}
    )
    return redirect(url_for("index"))


@app.route("/deletar/<id>")
def deletar(id):
    if not usuario_logado():
        return redirect(url_for("login"))
    deletar_transacao(ObjectId(id))
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
