from datetime import datetime
from flask import Blueprint, jsonify, request
from database.database import  ClienteModel, ClienteSchema, db
from flasgger import swag_from

clientes = Blueprint("clientes", __name__, url_prefix="/api/v1/clientes")

@clientes.route('/criarCliente', methods=['POST'], endpoint='criar_cliente')
@swag_from('../docs/cliente/criarCliente.yaml')
def criar_cliente():

    nome = request.json['nome']
    cpf = request.json['cpf']

    if ClienteModel.query.filter_by(cpf=cpf).first() is not None:
       return jsonify({'error': 'Esse cliente já foi cadastrado'}, 409)

    novo_cliente = ClienteModel(nome=nome, cpf=cpf)
    db.session.add(novo_cliente)
    db.session.commit()
    return jsonify({
        'id': novo_cliente.id,
        'nome': novo_cliente.nome,
        'cpf': novo_cliente.cpf
    }), 201

@clientes.get('/getCliente')
@swag_from('../docs/cliente/getCliente.yaml')
def get_cliente():
    cpf = request.args.get('cpf')
    cliente = ClienteModel.query.filter_by(cpf=cpf).first()
    cliente_schema = ClienteSchema()
    cliente_serialize = cliente_schema.dump(cliente)
    return jsonify(cliente_serialize)