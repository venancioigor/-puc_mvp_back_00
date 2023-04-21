from datetime import datetime
from flask import Blueprint, jsonify, request
from database.database import ContaModel, TransacaoModel, db
from flasgger import swag_from

transacoes = Blueprint("transacoes", __name__, url_prefix="/api/v1/transacoes")

@transacoes.route('/fazTransacao', methods=['POST'])
@swag_from('../docs/transacao/fazTransacao.yaml')
def criar_transacao():
    
    data = request.json
    conta = ContaModel.query.filter_by(conta=data['conta']).first()
    if not conta:
        return jsonify({'message': 'Conta não encontrada.'}), 404

    data_obj = datetime.strptime(data['data'], '%Y%m%d').date()
    transacao = TransacaoModel(id_conta=conta.id, data=data_obj, tipo=data['tipo'], descricao=data['descricao'], valor=data['valor'])
    db.session.add(transacao)
    db.session.commit()
    ##transacao.atualizar_saldo_conta() 
    return jsonify({'message': 'Transação feita com sucesso.'}), 201