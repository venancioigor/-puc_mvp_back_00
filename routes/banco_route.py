from flask import Blueprint, jsonify, request
from database.database import BancoModel, db
from flasgger import swag_from

bancos = Blueprint("bancos", __name__, url_prefix="/api/v1/bancos")


@bancos.route('/cadastrarBanco', methods=['POST'])
@swag_from('../docs/banco/cadastrarBanco.yaml')
def criar_banco():
    
    # Captura os dados do novo banco que serão enviados pelo usuário
    nome = request.json.get('nome')

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