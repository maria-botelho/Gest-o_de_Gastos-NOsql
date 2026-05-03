from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import sys

_client = None
_db = None


def conectar(uri="mongodb://localhost:27017", nome_banco="financeiro_app"):
    global _client, _db
    try:
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        _db = _client[nome_banco]
        return _db
    except ConnectionFailure as e:
        print(f"Falha ao conectar ao MongoDB: {e}")
        sys.exit(1)


def obter_db():
    if _db is None:
        raise RuntimeError("Banco não conectado. Chame conectar() primeiro.")
    return _db


def fechar_conexao():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
