from flask import Flask, render_template, request, redirect, url_for
from bson import ObjectId
from datetime import datetime
import calendar

# Importações dos teus módulos
from conexao import conectar, obter_db
from transacoes import inserir_transacao, buscar_transacoes_por_usuario, deletar_transacao
from relatorios import relatorio_dashboard
from usuarios import buscar_todos_usuarios
from contas import buscar_contas_por_usuario
from categorias import buscar_todas_categorias, buscar_categoria_por_nome

app = Flask(__name__)
conectar()
db = obter_db()

@app.route('/')
def index():
    usuarios = buscar_todos_usuarios()
    if not usuarios: 
        return "⚠️ Erro: Executa o 'dados_exemplo.py' primeiro."
    
    usuario_atual = usuarios[0]
    u_id = usuario_atual['_id']
    
    # Filtro de Data da URL
    hoje = datetime.now()
    mes_sel = int(request.args.get('mes', hoje.month))
    ano_sel = int(request.args.get('ano', hoje.year))

    # Cálculo do Saldo Dinâmico (Soma tudo até o final do mês selecionado)
    ultimo_dia = calendar.monthrange(ano_sel, mes_sel)[1]
    data_limite = datetime(ano_sel, mes_sel, ultimo_dia, 23, 59, 59)

    contas_brutas = buscar_contas_por_usuario(u_id)
    contas_finais = []

    for conta in contas_brutas:
        pipeline = [
            {"$match": {
                "conta_id": conta['_id'],
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
        conta['saldo_exibicao'] = res[0]['saldo'] if res else 0.0
        contas_finais.append(conta)

    return render_template('index.html', 
                           usuario=usuario_atual,
                           contas=contas_finais,
                           transacoes=buscar_transacoes_por_usuario(u_id),
                           dashboard=relatorio_dashboard(u_id, mes_sel, ano_sel),
                           categorias=buscar_todas_categorias(),
                           mes=mes_sel, ano=ano_sel)

@app.route('/add_transacao', methods=['POST'])
def add_transacao():
    u_id = ObjectId(request.form.get('usuario_id'))
    c_id = ObjectId(request.form.get('conta_id'))
    valor = float(request.form.get('valor'))
    tipo = request.form.get('tipo')
    desc = request.form.get('descricao')
    cat_nome = request.form.get('categoria')
    
    # Processamento da Data do Formulário
    data_str = request.form.get('data')
    data_dt = datetime.strptime(data_str, '%Y-%m-%d') if data_str else datetime.now()

    cat_obj = buscar_categoria_por_nome(cat_nome)
    icone = cat_obj['icone'] if cat_obj else "💰"
    
    inserir_transacao(u_id, c_id, valor, tipo, desc, cat_nome, icone, data_dt)
    return redirect(url_for('index'))

@app.route('/editar_completo', methods=['POST'])
def editar_completo():
    t_id = ObjectId(request.form.get('transacao_id'))
    data_str = request.form.get('data')
    data_dt = datetime.strptime(data_str, '%Y-%m-%d')
    
    db.transacoes.update_one(
        {"_id": t_id},
        {"$set": {
            "descricao": request.form.get('descricao'),
            "valor": float(request.form.get('valor')),
            "tipo": request.form.get('tipo'),
            "data": data_dt,
            "categoria.nome": request.form.get('categoria')
        }}
    )
    return redirect(url_for('index'))

@app.route('/deletar/<id>')
def deletar(id):
    deletar_transacao(ObjectId(id))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)