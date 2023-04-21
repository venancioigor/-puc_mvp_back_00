from flask import Blueprint, jsonify, request
from database.database import BancoModel, BancoSchema, db
from flasgger import swag_from

bancos = Blueprint("bancos", __name__, url_prefix="/api/v1/bancos")


@bancos.route('/cadastrarBanco', methods=['POST'])
@swag_from('../docs/banco/cadastrarBanco.yaml')
def criar_banco():
    data = request.json
    # Captura os dados do novo banco que serão enviados pelo usuário
    nome = data['nome']

    if BancoModel.query.filter_by(nome=nome).first() is not None:
       return jsonify({'error': 'Esse banco já foi cadastrado'}, 409)
    # Cria uma nova instância da classe "BancoModel"
    novo_banco = BancoModel(nome=nome)
    

    # Adiciona a nova instância à sessão do banco de dados
    db.session.add(novo_banco)

    # Salva as alterações na sessão do banco de dados
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'message': 'Erro ao criar banco.'}), 500

    # Retorna uma mensagem de sucesso para o usuário
    return jsonify({'message': 'Banco criado com sucesso.'}), 201

@bancos.get('/')
@swag_from('../docs/banco/retornaTodosBancos.yaml')
def get_all_bancos():
    bancos = BancoModel.query.all()
    bancos_schema = BancoSchema(many=True)
    bancos_serializado = bancos_schema.dump(bancos)
    return jsonify(bancos_serializado)


@bancos.get('/getBanco')
@swag_from('../docs/banco/getBanco.yaml')
def get_banco():
    nome = request.args.get('nome')
    banco = BancoModel.query.filter_by(nome=nome).first()
    if not banco:
        return jsonify({'Erro': 'Banco não encontrado'}), 404
    banco_schema = BancoSchema()
    banco_serializado = banco_schema.dump(banco)
    return jsonify(banco_serializado)

    




