from datetime import datetime
from flask import Blueprint, jsonify, request
from database.database import  ClienteModel, PorquinhoModel, db
from flasgger import swag_from

porquinhos = Blueprint("porquinhos", __name__, url_prefix="/api/v1/porquinhos")

@porquinhos.route('/criarPorquinho', methods=['POST'])
@swag_from('../docs/porquinho/criarPorquinho.yaml')
def criar_porquinho():
    data = request.json
    cpf = data['cpf']

    data_obj = datetime.strptime(data['data'], '%Y%m%d').date()

    # Consulta ao banco para encontrar o usuário com o CPF informado
    cliente = ClienteModel.query.filter_by(cpf=cpf).first()
    if not cliente:
        return jsonify({'message': 'Cliente não encontrado.'}), 404
    
    # Cria uma nova instância da classe "PorquinhoModel" com os dados informados pelo usuário
    nova_porquinho = PorquinhoModel(id_cliente=cliente.id, objetivo=data['objetivo'], valor = data['valor'], data=data_obj)

    # Salva a nova instância no banco de dados
    db.session.add(nova_porquinho)
    db.session.commit()

    return jsonify({'message': 'Conta porquinho aberta com sucesso.'}), 201