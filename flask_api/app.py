from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contactos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "correo": self.correo
        }


with app.app_context():
    db.create_all()


@app.route('/contactos', methods=['GET'])
def obtener_contactos():
    contactos = Contacto.query.all()
    return jsonify([c.to_dict() for c in contactos]), 200


@app.route('/contactos/<int:id>', methods=['GET'])
def obtener_contacto(id):
    contacto = Contacto.query.get(id)
    if not contacto:
        return jsonify({"error": "Contacto no encontrado"}), 404
    return jsonify(contacto.to_dict()), 200


@app.route('/contactos', methods=['POST'])
def crear_contacto():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON inválido o vacío"}), 400
    if not data.get('nombre') or not data.get('telefono'):
        return jsonify({"error": "nombre y telefono son obligatorios"}), 400

    nuevo = Contacto(
        nombre=data['nombre'],
        telefono=data['telefono'],
        correo=data.get('correo')
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


@app.route('/contactos/<int:id>', methods=['PUT'])
def actualizar_contacto(id):
    contacto = Contacto.query.get(id)
    if not contacto:
        return jsonify({"error": "Contacto no encontrado"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON inválido o vacío"}), 400

    contacto.nombre = data.get('nombre', contacto.nombre)
    contacto.telefono = data.get('telefono', contacto.telefono)
    contacto.correo = data.get('correo', contacto.correo)
    db.session.commit()
    return jsonify(contacto.to_dict()), 200


@app.route('/contactos/<int:id>', methods=['DELETE'])
def eliminar_contacto(id):
    contacto = Contacto.query.get(id)
    if not contacto:
        return jsonify({"error": "Contacto no encontrado"}), 404

    db.session.delete(contacto)
    db.session.commit()
    return jsonify({"mensaje": "Contacto eliminado"}), 200


@app.errorhandler(404)
def no_encontrado(e):
    return jsonify({"error": "Ruta no encontrada"}), 404


@app.errorhandler(500)
def error_interno(e):
    return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
