from datetime import datetime
from bson import ObjectId
from conexao import obter_db


def relatorio_extrato_detalhado(usuario_id, mes=None, ano=None):
    db = obter_db()

    filtro = {"usuario_id": usuario_id}
    if mes and ano:
        inicio = datetime(ano, mes, 1)
        fim = datetime(ano + 1, 1, 1) if mes == 12 else datetime(ano, mes + 1, 1)
        filtro["data"] = {"$gte": inicio, "$lt": fim}

    pipeline = [
        {"$match": filtro},
        {"$lookup": {
            "from": "contas",
            "localField": "conta_id",
            "foreignField": "_id",
            "as": "dados_conta",
        }},
        {"$unwind": "$dados_conta"},
        {"$project": {
            "_id": 1,
            "data": 1,
            "descricao": 1,
            "valor": 1,
            "tipo": 1,
            "categoria_nome": "$categoria.nome",
            "categoria_icone": "$categoria.icone",
            "conta_nome": "$dados_conta.nome",
            "conta_tipo": "$dados_conta.tipo",
        }},
        {"$sort": {"data": -1}},
    ]

    return list(db.transacoes.aggregate(pipeline))


def relatorio_dashboard(usuario_id, mes, ano):
    db = obter_db()

    inicio = datetime(ano, mes, 1)
    fim = datetime(ano + 1, 1, 1) if mes == 12 else datetime(ano, mes + 1, 1)

    pipeline = [
        {"$match": {
            "usuario_id": usuario_id,
            "data": {"$gte": inicio, "$lt": fim},
        }},
        {"$facet": {
            "total_saidas": [
                {"$match": {"tipo": "saída"}},
                {"$group": {"_id": None, "total": {"$sum": "$valor"}}},
                {"$project": {"_id": 0, "total": 1}},
            ],
            "total_entradas": [
                {"$match": {"tipo": "entrada"}},
                {"$group": {"_id": None, "total": {"$sum": "$valor"}}},
                {"$project": {"_id": 0, "total": 1}},
            ],
            "ranking_categorias": [
                {"$match": {"tipo": "saída"}},
                {"$group": {
                    "_id": "$categoria.nome",
                    "icone": {"$first": "$categoria.icone"},
                    "total_gasto": {"$sum": "$valor"},
                    "qtd_transacoes": {"$sum": 1},
                }},
                {"$sort": {"total_gasto": -1}},
                {"$limit": 5},
            ],
            "maior_transacao": [
                {"$sort": {"valor": -1}},
                {"$limit": 1},
                {"$project": {
                    "_id": 0,
                    "descricao": 1,
                    "valor": 1,
                    "tipo": 1,
                    "categoria_nome": "$categoria.nome",
                    "data": 1,
                }},
            ],
        }},
    ]

    resultado = list(db.transacoes.aggregate(pipeline))
    return resultado[0] if resultado else {}
