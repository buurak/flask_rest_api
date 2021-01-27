from flask import Flask, request, jsonify
import json
import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

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
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    new_product = Product(name, description, price, qty)

    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)


    # perm_address = request.form['Permanent address']
    # curr_address = request.form['current Address']
    # mobile = request.form['Mobile']
    # name = request.form['Name']
    # pets = request.form['Pets']

    # new_usr = {
    #     'Address':{
    #         'Permanent address':perm_address,
    #         'current Address':curr_address
    #     },
    #     'Boolean':true,
    #     'Mobile':mobile,
    #     'Name':name,
    #     'Pets':pets
    # }

    

if __name__ == '__main__':
    app.run(host='localhost',port=8000, debug=True)