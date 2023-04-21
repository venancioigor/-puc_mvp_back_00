from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from database.database import  db, ma
from config.swagger import template, swagger_config
from routes.banco_route import bancos
from routes.conta_route import contas
from routes.transacao_route import transacoes
from routes.cliente_route import clientes

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Cofre.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Adicionar o bloco "definitions" no Swagger
app.config['SWAGGER'] = {
    'title': 'Meu cofre - API',
    'uiversion': 3
            }

swagger = Swagger(app, template=template, config=swagger_config)

db.app=app
db.init_app(app)
ma.init_app(app)

app.register_blueprint(bancos)
app.register_blueprint(contas)
app.register_blueprint(transacoes)
app.register_blueprint(clientes)

# Criar as rotas da API
# app.add_url_rule('/criarCliente', methods=['POST'], view_func=criar_cliente)

# Executar o aplicativo Flask
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

