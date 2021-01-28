from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from rq import Queue
from celeryconfig import *
import json
import os
import time


# Init app
app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)

@celery.task()
def add_together(a, b):
    return a + b

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:12345@localhost:5432/api"

# Inıt db
db = SQLAlchemy(app)

#Init ma
ma = Marshmallow(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id','name','description','price','qty')

product_schema = ProductSchema()
product_schemas = ProductSchema(many=True)
        

@app.route('/product', methods=['POST'])
@celery.task()
def add_product_api():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']
    new_product = Product(name, description, price, qty)
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product)


@app.route('/product', methods=['GET'])
def get_products():
  all_products = Product.query.all()
  result = product_schemas.dump(all_products)
  return jsonify(result)


@app.route('/product/<id>', methods=['GET'])
def get_product(id):
  product = Product.query.get(id)
  return product_schema.jsonify(product)

@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']
    product.name = name
    product.description = description
    product.price = price
    product.qty = qty
    new_product = Product(name,description,price,qty)
    db.session.commit()
    return product_schema.jsonify(new_product)

@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
  product = Product.query.get(id)
  db.session.delete(product)
  db.session.commit()
  return product_schema.jsonify(product)
    

if __name__ == '__main__':
    app.run(host='localhost',port=8000, debug=True)