from datetime import date
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields as ma_fields, ValidationError
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

