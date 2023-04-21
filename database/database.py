from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema
from datetime import date, datetime

db = SQLAlchemy()
ma = Marshmallow()

# CTRL + M + R --- cria region

# region SaldoConta
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

# endregion

# region Banco

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
# endregion

# region Conta
class ContaModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conta = db.Column(db.String(9), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente_model.id'), nullable=False)
    id_banco = db.Column(db.Integer, db.ForeignKey('banco_model.id'), nullable=False)
    saldo = db.Column(db.Numeric(10,2), nullable=False)

    #saldo_conta = db.relationship('SaldoContaModel', backref='conta_model', uselist=False, lazy=True)   
    banco = db.relationship('BancoModel', backref='contas')
   
    def __repr__(self):
        return f'<ContaModel {self.id}>'
    
    def transferir_valor_entre_conta_origem_para_destino(self, conta_destino, valor_origem):
        if self.saldo < valor_origem:
            return {'error': 'Saldo insuficiente na conta de origem'}
        
        self.saldo -= valor_origem
        conta_destino.saldo += valor_origem
        
        #db.session.commit()

        return {'mensagem':'Transferência concluída com sucesso'}

# Definir o esquema de serialização
class ContaSchema(SQLAlchemySchema):
    class Meta:
        model = ContaModel
        include_fk = True

    id = ma.auto_field()
    id_cliente = ma.auto_field()
    id_banco = ma.auto_field()
    conta = ma.auto_field()
    saldo = ma.auto_field()


# endregion

# region Saldo
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
    
# endregion

# region Porquinho
class PorquinhoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente_model.id'), nullable=False)
    objetivo = db.Column(db.String(100), nullable=False)
    saldo = db.Column(db.Numeric(10,2), nullable=False)
    #data = db.Column(db.Date, default=date.today, nullable=False) 

    def __repr__(self):
        return f'<PorquinhoModel {self.id}>'
    
    def transferir_valor_entre_conta_origem_para_destino(self, porquinho_destino, valor_origem):
        if self.saldo < valor_origem:
            return {'error': 'Saldo insuficiente na conta de origem'}
        
        self.saldo -= valor_origem
        porquinho_destino.saldo += valor_origem
        

        #db.session.commit()

        return {'mensagem':'Transferência concluída com sucesso'}



class PorquinhoSchema(SQLAlchemySchema):
    class Meta:
        model = PorquinhoModel

    id = ma.auto_field()
    id_cliente = ma.auto_field()
    objetivo = ma.auto_field()
    saldo = ma.auto_field()
    #data = ma.auto_field() 
  

# endregion Banco

# region Cliente
class ClienteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)

    contas = db.relationship('ContaModel', backref='cliente', lazy=True)
    porquinhos = db.relationship('PorquinhoModel', backref='cliente', lazy=True)
    saldo = db.relationship('SaldoModel', backref='cliente', uselist=False, lazy=True)

    def __repr__(self):
        return f'<ClienteModel {self.id}>'


class ClienteSchema(SQLAlchemySchema):
    class Meta:
        model = ClienteModel

    id = ma.auto_field()
    nome = ma.auto_field()
    cpf = ma.auto_field()

# endregion



# region Transacao
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
# endregion