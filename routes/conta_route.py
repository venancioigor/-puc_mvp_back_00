from flask import Blueprint, jsonify, request
from database.database import BancoModel, ClienteModel, ContaModel, db
from flasgger import swag_from

contas = Blueprint("contas", __name__, url_prefix="/api/v1/contas")

@contas.route('/abrirConta', methods=['POST'])
@swag_from('../docs/conta/abrirConta.yaml')
def cadastrar_conta():
    
    cpf = request.json.get('cpf')
    nome_banco = request.json.get('nome_banco')

    # Consulta ao banco para encontrar o usuário com o CPF informado
    cliente = ClienteModel.query.filter_by(cpf=cpf).first()
    if not cliente:
        return jsonify({'message': 'Cliente não encontrado.'}), 404

    
    # Consulta ao banco para encontrar o banco com o nome informado
    banco = BancoModel.query.filter_by(nome=nome_banco).first()
    if not banco:
        return jsonify({'message': 'Banco não encontrado.'}), 404

    # Cria uma nova instância da classe "ContaModel" com os dados informados pelo usuário
    nova_conta = ContaModel(id_cliente=cliente.id, id_banco=banco.id, conta=request.json.get('conta'))

    # Salva a nova instância no banco de dados
    db.session.add(nova_conta)
    db.session.commit()

    return jsonify({'message': 'Conta aberta com sucesso.'}), 201