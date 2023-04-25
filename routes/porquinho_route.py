from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from database.database import  ClienteModel, PorquinhoModel, PorquinhoSchema, db
from flasgger import swag_from

porquinhos = Blueprint("porquinhos", __name__, url_prefix="/api/porquinhos")

@porquinhos.route('/criarPorquinho', methods=['POST'])
@swag_from('../docs/porquinho/criarPorquinho.yaml')
def criar_porquinho():
    data = request.json
    cpf = data['cpf']

    # Consulta ao banco para encontrar o usuário com o CPF informado
    cliente = ClienteModel.query.filter_by(cpf=cpf).first()
    if not cliente:
        return jsonify({'message': 'Cliente não encontrado.'}), 404
    
    # Cria uma nova instância da classe "PorquinhoModel" com os dados informados pelo usuário
    nova_porquinho = PorquinhoModel(id_cliente=cliente.id, objetivo=data['objetivo'], saldo = data['saldo'])#, data=data_obj)

    # Salva a nova instância no banco de dados
    db.session.add(nova_porquinho)
    db.session.commit()

    return jsonify({'message': 'Conta porquinho aberta com sucesso.'}), 201


@porquinhos.get('/getAllPorquinhos')
@swag_from('../docs/porquinho/getAllPorquinhos.yaml')
def get_all_porquinhos():
    cpf = request.args.get('cpf')
    cliente = ClienteModel.query.filter_by(cpf=cpf).first()
    print(cliente)
    if not cliente:
        return jsonify({'message': 'Cliente não encontrado.'}), 404
    
    porquinhos = PorquinhoModel.query.filter_by(id_cliente=cliente.id).all()
    porquinhos_schema = PorquinhoSchema(many=True)
    porquinhos_serializado = porquinhos_schema.dump(porquinhos)

    return jsonify(porquinhos_serializado)
    
@porquinhos.route('/porquinho/transferirValorEntrePorquinho', methods=['POST'])
@swag_from('../docs/porquinho/transferirValorEntrePorquinhos.yaml')
def transferir_valor_entre_contas_porquinho():
    dados = request.json

    id_origem = dados['id_origem']
    id_destino = dados['id_destino']
    cpf_cliente = dados['cpf']
    valor = dados['valor_origem']

    if valor <= 0:
        return jsonify({'error': 'O valor deve ser maior que 0'})

    cliente = ClienteModel.query.filter_by(cpf=cpf_cliente).first()
    if not cliente:
        return jsonify({'error': 'Cliente não existe'})
    
    porquinho_origem = PorquinhoModel.query.filter_by(id=id_origem, id_cliente=cliente.id).first()
    porquinho_destino = PorquinhoModel.query.filter_by(id=id_destino, id_cliente=cliente.id).first()

    if not porquinho_origem:
            return {'error': 'Porquinho origem não encontrado'}
    if not porquinho_destino:
            return {'error': 'Porquinho destino não encontrado'}
    try:
        porquinho_origem.transferir_valor_entre_conta_origem_para_destino(porquinho_destino, valor)
        db.session.commit()
        return jsonify({'message': 'Transferência efetuada com sucesso'}), 200
    except ValueError as e:
        db.session.rollback()
    return jsonify({'error': str(e)}), 400


    
@porquinhos.delete('/deletarPorquinho')
@swag_from('../docs/porquinho/deletarPorquinho.yaml')
def deletar_porquinho():
     id_porquinho = request.args.get('id_porquinho')
     cpf = request.args.get('cpf')
     cliente = ClienteModel.query.filter_by(cpf=cpf).first()
     porquinho = PorquinhoModel.query.filter_by(id=id_porquinho,id_cliente=cliente.id).first()
     if not porquinho:
          return jsonify({'error':'Porquinho não encontrado'}), 404
     db.session.delete(porquinho)
     db.session.commit()

     return jsonify({'message':'Porquinho deletado com sucesso'}), 200

@porquinhos.get('/getSaldoTotalPorquinhos')
@swag_from('../docs/porquinho/getSaldoTotalPorquinho.yaml')
def get_saldo_total_contas():
     cpf = request.args.get('cpf')
     cliente = ClienteModel.query.filter_by(cpf=cpf).first()
     if not cliente:
          return jsonify({'error':'Cliente não encontrado'}), 404
     saldo_porquinhos = db.session.query(func.sum(PorquinhoModel.saldo)).filter_by(id_cliente=cliente.id).scalar()
     
     return jsonify({'saldo':saldo_porquinhos}), 200