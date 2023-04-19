from app import app, db
from flask import jsonify, request
from flask import Flask, request, jsonify
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemySchema
from flask_cors import CORS
from models import ContaModel, ContaSchema, TransacaoModel, TransacaoSchema

conta_schema = ContaSchema()
transacao_schema = TransacaoSchema()




#