from datetime import datetime
from bson import ObjectId
from conexao import obter_db


def inserir_conta(usuario_id, nome, tipo, saldo=0.0):
    db = obter_db()
    doc = {
        "usuario_id": usuario_id,
        "nome": nome,
        "tipo": tipo,
        "saldo": saldo,
        "criado_em": datetime.utcnow(),
    }
    resultado = db.contas.insert_one(doc)
    return resultado.inserted_id


def buscar_conta_por_id(conta_id):
    db = obter_db()
    return db.contas.find_one({"_id": conta_id})


def buscar_contas_por_usuario(usuario_id):
    db = obter_db()
    return list(db.contas.find({"usuario_id": usuario_id}))


def atualizar_saldo_conta(conta_id, valor):
    db = obter_db()
    db.contas.update_one({"_id": conta_id}, {"$inc": {"saldo": valor}})


def renomear_conta(conta_id, novo_nome):
    db = obter_db()
    db.contas.update_one({"_id": conta_id}, {"$set": {"nome": novo_nome}})


def deletar_conta(conta_id):
    db = obter_db()
    resultado = db.contas.delete_one({"_id": conta_id})
    return resultado.deleted_count
