
from app import db, ma, SQLAlchemySchema

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