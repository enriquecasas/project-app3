import os
from datetime import datetime
from dateutil import parser as datetime_parser
from dateutil.tz import tzutc
from flask import Flask, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from .utils import split_url

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)

db = SQLAlchemy(app)

class ValidationError(ValueError):
    pass



class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    apellido = db.Column(db.String(100))
    pedidos = db.relationship('Pedidos', backref='cliente', lazy='dynamic')

    def get_url(self):
    return url_for('get_cliente', id=self.id, _external=True)    

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'name': self.name,
            'orders_url': url_for('get_cliente_pedidos', id=self.id,
                                  _external=True)
        }

    def import_data(self, data):
        try:
            self.name = data['name']
        except KeyError as e:
            raise ValidationError('Invalid cliente: missing ' + e.args[0])
        return self



class Pedido(db.Model):
    __tablename__='pedidos'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'),
                            index=True)
    pedidoproductos = db.relationship('Pedidoproducto', backref='pedido', lazy='dynamic',
                            cascade='all, delete-orphan')
    
    def get_url(self):
        return url_for('get_pedido', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'cliente_url': self.cliente.get_url(),
            'date': self.date.isoformat() + 'Z',
            'items_url': url_for('get_productopedidos', id=self.id,
                                 _external=True)
        }

    def import_data(self, data):
        try:
            self.date = datetime_parser.parse(data['date']).astimezone(
                tzutc()).replace(tzinfo=None)
        except KeyError as e:
            raise ValidationError('Invalid pedido: missing ' + e.args[0])
        return self


class Producto(db.Model):
    __tablename__='pedidoproductos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    desciption = db.Column(db.String(200),index = True)
    precio = db.Column(db.String(10),index=True)
    pedidoproductos = db.relationship('Pedidoproductos', backref='producto', lazy='dynamic')

    def get_url(self):
        return url_for('get_producto', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'name': self.name
        }

    def import_data(self, data):
        try:
            self.name = data['name']
        except KeyError as e:
            raise ValidationError('Invalid producto: missing ' + e.args[0])
        return self

class Pedidoproducto(db.Model):
    __tablename__='pedidoproductos'
    id = db.Column(db.Integer, primary_key=True)
    pedidos_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'),
                           index=True)
    quantity = db.Column(db.Integer)

     def get_url(self):
        return url_for('get_pedidoproducto', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'pedido_url': self.order.get_url(),
            'producto_url': self.product.get_url(),
            'quantity': self.quantity
        }

    def import_data(self, data):
        try:
            endpoint, args = split_url(data['producto_url'])
            self.quantity = int(data['quantity'])
        except KeyError as e:
            raise ValidationError('Invalid order: missing ' + e.args[0])
        if endpoint != 'get_producto' or not 'id' in args:
            raise ValidationError('Invalid producto URL: ' +
                                  data['producto_url'])
        self.product = Product.query.get(args['id'])
        if self.product is None:
            raise ValidationError('Invalid producto URL: ' +
                                  data['producto_url'])
        return self


@app.route('/clientes/', methods=['GET'])
def get_clientes():
    return jsonify({'clientes': [cliente.get_url() for cliente in
                                  Cliente.query.all()]})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)