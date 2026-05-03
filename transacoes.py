from datetime import datetime
from bson import ObjectId
from conexao import obter_db
from contas import atualizar_saldo_conta
from usuarios import atualizar_saldo_usuario


def inserir_transacao(usuario_id, conta_id, valor, tipo, descricao, categoria_nome, categoria_icone="💰", data=None):
    db = obter_db()
    data = data or datetime.utcnow()

    doc = {
        "usuario_id": usuario_id,
        "conta_id": conta_id,
        "valor": valor,
        "tipo": tipo,
        "descricao": descricao,
        "data": data,
        "categoria": {
            "nome": categoria_nome,
            "icone": categoria_icone,
        },
    }
    resultado = db.transacoes.insert_one(doc)

    incremento = valor if tipo == "entrada" else -valor
    atualizar_saldo_conta(conta_id, incremento)
    atualizar_saldo_usuario(usuario_id, incremento)

    return resultado.inserted_id


def buscar_transacao_por_id(transacao_id):
    db = obter_db()
    return db.transacoes.find_one({"_id": transacao_id})


def buscar_transacoes_por_usuario(usuario_id):
    db = obter_db()
    return list(db.transacoes.find({"usuario_id": usuario_id}).sort("data", -1))


def buscar_transacoes_por_mes(usuario_id, mes, ano):
    db = obter_db()
    inicio = datetime(ano, mes, 1)
    fim = datetime(ano + 1, 1, 1) if mes == 12 else datetime(ano, mes + 1, 1)
    return list(db.transacoes.find({
        "usuario_id": usuario_id,
        "data": {"$gte": inicio, "$lt": fim},
    }).sort("data", -1))


def buscar_transacoes_por_categoria(usuario_id, categoria):
    db = obter_db()
    return list(db.transacoes.find({
        "usuario_id": usuario_id,
        "categoria.nome": categoria,
    }).sort("data", -1))


def atualizar_descricao_transacao(transacao_id, nova_descricao):
    db = obter_db()
    db.transacoes.update_one({"_id": transacao_id}, {"$set": {"descricao": nova_descricao}})


def deletar_transacao(transacao_id):
    db = obter_db()
    resultado = db.transacoes.delete_one({"_id": transacao_id})
    return resultado.deleted_count


def deletar_transacoes_por_usuario(usuario_id):
    db = obter_db()
    resultado = db.transacoes.delete_many({"usuario_id": usuario_id})
    return resultado.deleted_count
