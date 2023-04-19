from flask import Flask, request, jsonify
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema
from flasgger import Swagger
from flask_cors import CORS
from routes import *
from models import *

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
swagger = Swagger(app)



# Definir os modelos
class SaldoContaModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_conta = db.Column(db.Integer, db.ForeignKey('conta_model.id'), nullable=False)
    tipo = db.Column(db.String(1), nullable=False)  
    saldo = db.Column(db.Numeric(10,2), nullable=False)
    data = db.Column(db.Date, default=date.today, nullable=False)

    def __repr__(self):
        return f'<SaldoContaModel {self.id}>'


class SaldoContaSchema(SQLAlchemySchema):
    class Meta:
        model = SaldoContaModel

    id = ma.auto_field()
    id_conta = ma.auto_field()
    tipo = ma.auto_field()
    saldo = ma.auto_field()
    data = ma.auto_field()


class ContaModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conta = db.Column(db.String(9), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente_model.id'), nullable=False)
    id_banco = db.Column(db.Integer, db.ForeignKey('banco_model.id'), nullable=False)

    saldo_conta = db.relationship('SaldoContaModel', backref='conta_model', uselist=False, lazy=True)   
   
    def __repr__(self):
        return f'<ContaModel {self.id}>'

# Definir o esquema de serialização
class ContaSchema(SQLAlchemySchema):
    class Meta:
        model = ContaModel

    id = ma.auto_field()
    id_cliente = ma.auto_field()
    id_banco = ma.auto_field()
    conta = ma.auto_field()

class SaldoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente_model.id'), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)

class SaldoSchema(SQLAlchemySchema):
    class Meta:
        model = SaldoModel

    id = ma.auto_field()
    id_cliente = ma.auto_field()
    valor = ma.auto_field()
    

class ClienteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)

    contas = db.relationship('ContaModel', backref='cliente', lazy=True)
    saldo = db.relationship('SaldoModel', backref='cliente', uselist=False, lazy=True)

    def __repr__(self):
        return f'<ClienteModel {self.id}>'


class ClienteSchema(SQLAlchemySchema):
    class Meta:
        model = ClienteModel

    id = ma.auto_field()
    nome = ma.auto_field()
    cpf = ma.auto_field()



class BancoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
   
    def __repr__(self):
        return f'<BancoModel {self.id}>'

# Definir o esquema de serialização
class BancoSchema(SQLAlchemySchema):
    class Meta:
        model = BancoModel

    id = ma.auto_field()
    nome = ma.auto_field()


class TransacaoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_conta = db.Column(db.Integer, db.ForeignKey('conta_model.id'), nullable=False)
    tipo = db.Column(db.String(1), nullable=False)  
    valor = db.Column(db.Numeric(10,2), nullable=False)
    descricao = db.Column(db.String(150), nullable=False)  
    data = db.Column(db.Date, default=date.today, nullable=False)

    def atualizar_saldo_conta(self):
        conta = ContaModel.query.get(self.id_conta)
        saldo_conta = SaldoContaModel.query.filter_by(id_conta=self.id_conta).first()
        if self.tipo == 'C':
            saldo_conta.saldo += self.valor
        elif self.tipo == 'D':
            saldo_conta.saldo -= self.valor
        db.session.add(saldo_conta)
        db.session.commit()

class TransacaoSchema(SQLAlchemySchema):
    class Meta:
        model = TransacaoModel

    id = ma.auto_field()
    id_conta = ma.auto_field()
    tipo = ma.auto_field() 
    valor = ma.auto_field()
    descricao = ma.auto_field()
    data = ma.auto_field()


#Adicionar o bloco "definitions" no Swagger
app.config['SWAGGER'] = {
    'title': 'Meu dinheiro - API',
    'uiversion': 3,
    'definitions': {
        'Cliente': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer',
                    'description': 'O ID do cliente'
                },
                'nome': {
                    'type': 'string',
                    'description': 'O nome do cliente'
                },
                'cpf': {
                    'type': 'string',
                    'description': 'O cpf do cliente'
                }
            }
        }
    }
}




# Criar as rotas da API

@app.route('/criarCliente', methods=['POST'])
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

@app.route('/cadastrarBanco', methods=['POST'])
def criar_banco():
    """
    Cria um novo banco

    Esta rota permite criar um novo banco, fornecendo o nome como entrada.

    ---
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            nome:
              type: string
        required: true
        description: O nome do banco que deve ser registrado
    responses:
      201:
        description: O banco foi registrado com sucesso
        schema:
          type: object
          properties:
            id:
              type: integer
              description: O ID do banco criado
            nome:
              type: string
              description: O nome do banco registrado
      400:
        description: Os dados de entrada são inválidos
    """
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



@app.route('/abrirConta', methods=['POST'])
def cadastrar_conta():
    """
    Abre uma nova conta

    Esta rota permite abrir uma nova conta.

    ---
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            conta:
              type: string
            cpf:
              type: string
            nome_banco:
              type: string
        required: true
        description: Os dados da conta que será aberta.
    responses:
      201:
        description: A conta foi aberta com sucesso.
        schema:
          type: object
          properties:
            id:
              type: integer
              description: O ID da conta criado
            conta:
              type: string
              description: O número da conta do cliente 
            cpf:
              type: string
              description: O cpf do cliente que referencia a conta
            nome_banco:
              type: string
              description: O nome do banco dessa conta e cliente
      400:
        description: Os dados de entrada são inválidos
    """
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


@app.route('/fazTransacao', methods=['POST'])
def criar_transacao():
    """
        Faz uma nova transação

        Esta rota permite que o cliente faça uma nova transação.

        ---
        parameters:
          - name: body
            in: body
            schema:
              type: object
              properties:
                conta:
                  type: string
                descricao:
                  type: string
                tipo:
                  type: string
                data:
                  type: string
                valor:
                  type: number

            required: true
            description: Os dados da transação que foi realizada.
        responses:
          201:
            description: A transação foi feita com sucesso..
            schema:
              type: object
              properties:
                id:
                  type: integer
                  description: O ID da transação realizada
          400:
            description: Os dados de entrada são inválidos
    """
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


# Executar o aplicativo Flask
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
