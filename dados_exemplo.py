from datetime import datetime, timedelta
from conexao import conectar, fechar_conexao
from categorias import inserir_categorias_padrao
from usuarios import inserir_usuario
from contas import inserir_conta
from transacoes import inserir_transacao


def popular():
    db = conectar()
    print("Limpando dados antigos...")
    db.usuarios.drop()
    db.contas.drop()
    db.transacoes.drop()
    db.categorias.drop()

    print("Inserindo categorias...")
    inserir_categorias_padrao()

    print("Criando usuário de exemplo...")
    uid = inserir_usuario("Ana Silva", "ana@email.com", "123456")
    cid_corrente = inserir_conta(uid, "Nubank Corrente", "corrente")
    cid_poupanca = inserir_conta(uid, "Itaú Poupança", "poupança")

    hoje = datetime.now()

    print("Lançando transações...")
    inserir_transacao(uid, cid_corrente, 5500.0, "entrada", "Salário Maio", "Salário", "💼", hoje - timedelta(days=5))
    inserir_transacao(uid, cid_poupanca, 800.0, "entrada", "Renda Extra Freela", "Outros", "💰", hoje - timedelta(days=2))
    inserir_transacao(uid, cid_corrente, 320.0, "saída", "Supermercado Pão de Açúcar", "Alimentação", "🍔", hoje - timedelta(days=4))
    inserir_transacao(uid, cid_corrente, 1200.0, "saída", "Aluguel Apartamento", "Moradia", "🏠", hoje - timedelta(days=3))
    inserir_transacao(uid, cid_corrente, 200.0, "saída", "Academia SmartFit", "Saúde", "💊", hoje - timedelta(days=1))

    print("Concluído! Agora inicie o app.py.")
    fechar_conexao()


if __name__ == "__main__":
    popular()
