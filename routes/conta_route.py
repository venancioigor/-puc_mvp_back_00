from flask import Blueprint, jsonify, request, abort, Response
from sqlalchemy import func
from database.database import BancoModel, ClienteModel, ContaModel, ContaSchema, db
from flasgger import swag_from

contas = Blueprint("contas", __name__, url_prefix="/api/contas")

@contas.route('/abrirConta', methods=['POST', 'OPTIONS'], endpoint='cadastrar_conta')
@swag_from('../docs/conta/abrirConta.yaml')
def cadastrar_conta():
    if request.method == "OPTIONS":
        res = Response()
        res.headers['X-Content-Type-Options'] = '*'
        return res
     
    cpf = request.json.get('cpf')
    id_banco = request.json.get('id_banco')
    saldo = request.json.get('saldo')
    conta=request.json.get('conta')

    # Consulta ao banco para encontrar o usuário com o CPF informado
    cliente = ClienteModel.query.filter_by(cpf=cpf).first()
    if not cliente:
        return abort({'message': 'Cliente não encontrado.'}), 404

    if ContaModel.query.filter_by(id_cliente=cliente.id, conta=conta).first() is not None:
       return abort({'error': 'Essa conta já foi cadastrada'}, 409)
    
    # Consulta ao banco para encontrar o banco com o nome informado
    banco = BancoModel.query.get(id_banco)
    if not banco:
        return abort({'message': 'Banco não encontrado.'}), 404

    # Cria uma nova instância da classe "ContaModel" com os dados informados pelo usuário
    nova_conta = ContaModel(id_cliente=cliente.id, id_banco=banco.id, conta=conta, saldo=saldo)
    # Salva a nova instância no banco de dados
    db.session.add(nova_conta)
    db.session.commit()

    return jsonify({'message': 'Conta aberta com sucesso.'}), 201


@contas.get('/getContasPorCliente')
@swag_from('../docs/conta/getContasPorCliente.yaml')
def get_contas_por_cliente():
    cpf = request.args.get('cpf')

    cliente = ClienteModel.query.filter_by(cpf=cpf).first()
    if not cliente:
        return jsonify({'message': 'Cliente não encontrado.'}), 404
    
    contas = ContaModel.query.filter_by(id_cliente=cliente.id).all()
    contas_schema = ContaSchema(many=True)
    contas_serializadas = contas_schema.dump(contas)
    return jsonify(contas_serializadas)

@contas.route('/transferirValorEntreContas', methods=['POST'])
@swag_from('../docs/conta/transferirValorEntreContas.yaml')
def transferir_valor_entre_contas():
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
    
    conta_origem = ContaModel.query.filter_by(id=id_origem, id_cliente = cliente.id).first()
    conta_destino = ContaModel.query.filter_by(id=id_destino, id_cliente = cliente.id).first()

    if not conta_origem:
            return {'error': 'Conta origem não encontrada'}
    if not conta_destino:
            return {'error': 'Conta destino não encontrada'}
    try:
        conta_origem.transferir_valor_entre_conta_origem_para_destino(conta_destino, valor)
        db.session.commit()
        return jsonify({'message': 'Transferência efetuada com sucesso'}), 200
    except ValueError as e:
        db.session.rollback()
    return jsonify({'error': str(e)}), 400


    
@contas.delete('/deletarConta')
@swag_from('../docs/conta/deletarConta.yaml')
def deletar_porquinho():
     id_conta = request.args.get('id_conta')
     cpf = request.args.get('cpf')
     cliente = ClienteModel.query.filter_by(cpf=cpf).first()
     conta = ContaModel.query.filter_by(id=id_conta,id_cliente=cliente.id).first()
     if not conta:
          return jsonify({'error':'Conta não encontrada'}), 404
     db.session.delete(conta)
     db.session.commit()

     return jsonify({'message':'Conta deletada com sucesso'}), 200

@contas.get('/getSaldoTotalContas')
@swag_from('../docs/conta/getSaldoTotalContas.yaml')
def get_saldo_total_contas():
     cpf = request.args.get('cpf')
     cliente = ClienteModel.query.filter_by(cpf=cpf).first()
     if not cliente:
          return jsonify({'error':'Cliente não encontrado'}), 404
     saldo_contas = db.session.query(func.sum(ContaModel.saldo)).filter_by(id_cliente=cliente.id).scalar()
     
     return jsonify({'saldo':saldo_contas}), 200