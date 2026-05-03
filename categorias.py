from bson import ObjectId
from conexao import obter_db


def inserir_categoria(nome, icone="📦", cor="#888888"):
    db = obter_db()
    existente = db.categorias.find_one({"nome": nome})
    if existente:
        return existente["_id"]
    doc = {"nome": nome, "icone": icone, "cor": cor}
    resultado = db.categorias.insert_one(doc)
    return resultado.inserted_id


def inserir_categorias_padrao():
    categorias = [
        ("Alimentação",   "🍔", "#FF6B6B"),
        ("Transporte",    "🚗", "#4ECDC4"),
        ("Lazer",         "🎉", "#FFE66D"),
        ("Saúde",         "💊", "#A8E6CF"),
        ("Educação",      "📚", "#88D8FF"),
        ("Moradia",       "🏠", "#C9B8FF"),
        ("Salário",       "💼", "#95E17D"),
        ("Investimentos", "📈", "#FFB347"),
        ("Outros",        "💰", "#D3D3D3"),
    ]
    for nome, icone, cor in categorias:
        inserir_categoria(nome, icone, cor)


def buscar_todas_categorias():
    db = obter_db()
    return list(db.categorias.find())


def buscar_categoria_por_nome(nome):
    db = obter_db()
    return db.categorias.find_one({"nome": nome})


def atualizar_icone_categoria(nome, novo_icone):
    db = obter_db()
    db.categorias.update_one({"nome": nome}, {"$set": {"icone": novo_icone}})


def deletar_categoria(nome):
    db = obter_db()
    resultado = db.categorias.delete_one({"nome": nome})
    return resultado.deleted_count
