from app import app, db, ClienteModel
from flask import request, jsonify

@app.route('/criarCliente', methods=['POST'], endpoint='criar_cliente')
def criar_cliente():
    """
    Cria um novo cliente

    Esta rota permite criar um novo cliente, fornecendo o nome e CPF como entrada.

    ---
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            nome:
              type: string
            cpf:
              type: string
        required: true
        description: O nome do cliente, com cpf, que deve ser criado
    responses:
      201:
        description: O cliente foi criado com sucesso
        schema:
          type: object
          properties:
            id:
              type: integer
              description: O ID do cliente criado
            nome:
              type: string
              description: O nome do cliente criado
            cpf:
              type: string
              description: O cpf do cliente criado
      400:
        description: Os dados de entrada são inválidos
    """
    nome = request.json['nome']
    cpf = request.json['cpf']
    novo_cliente = ClienteModel(nome=nome, cpf=cpf)
    db.session.add(novo_cliente)
    db.session.commit()
    return jsonify({
        'id': novo_cliente.id,
        'nome': novo_cliente.nome,
        'cpf': novo_cliente.cpf
    }), 201