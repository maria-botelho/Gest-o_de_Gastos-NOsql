from datetime import datetime
from bson import ObjectId
from conexao import obter_db


def inserir_usuario(nome, email, senha):
    db = obter_db()
    doc = {
        "nome": nome,
        "email": email,
        "senha": senha,
        "metas_mensais": [],
        "criado_em": datetime.utcnow(),
    }
    resultado = db.usuarios.insert_one(doc)
    return resultado.inserted_id


def buscar_usuario_por_email(email):
    db = obter_db()
    return db.usuarios.find_one({"email": email})


def buscar_usuario_por_id(usuario_id):
    db = obter_db()
    return db.usuarios.find_one({"_id": usuario_id})


def buscar_todos_usuarios():
    db = obter_db()
    return list(db.usuarios.find())


def atualizar_saldo_usuario(usuario_id, valor):
    db = obter_db()
    db.usuarios.update_one({"_id": usuario_id}, {"$inc": {"saldo_total": valor}})


def adicionar_meta_mensal(usuario_id, categoria, valor_limite, mes, ano):
    db = obter_db()
    meta = {"categoria": categoria, "valor_limite": valor_limite, "mes": mes, "ano": ano}
    db.usuarios.update_one({"_id": usuario_id}, {"$push": {"metas_mensais": meta}})


def remover_meta_mensal(usuario_id, categoria, mes, ano):
    db = obter_db()
    db.usuarios.update_one(
        {"_id": usuario_id},
        {"$pull": {"metas_mensais": {"categoria": categoria, "mes": mes, "ano": ano}}}
    )


def deletar_usuario(usuario_id):
    db = obter_db()
    resultado = db.usuarios.delete_one({"_id": usuario_id})
    return resultado.deleted_count
