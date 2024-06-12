from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import string
import random
import os

app = Flask(__name__)

# Crear el directorio instance si no existe
if not os.path.exists('instance'):
    os.makedirs('instance')

# Ruta absoluta para la base de datos SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance/cortaurl.sqlite')
database_uri = f'sqlite:///{db_path}'

# Configuración de la base de datos usando create_engine
engine = create_engine(database_uri, pool_pre_ping=True)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, engine_options={'pool_pre_ping': True})

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(512), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)

def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# Crear tablas de la base de datos en la inicialización de la aplicación
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return jsonify({"message": "¡Bienvenido a CortaURL!"})

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    long_url = data.get("url")
    if not long_url:
        return jsonify({"error": "No URL provided"}), 400

    short_code = generate_short_code()
    new_url = URL(original_url=long_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()

    short_url = f"https://CortaURL.com/{short_code}"
    return jsonify({"message": "CortaURL", "short_url": short_url})

@app.route('/<short_code>')
def redirect_to_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        return redirect(url.original_url)
    return jsonify({"error": "Invalid URL"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Asegurarse de que el puerto esté configurado
    app.run(debug=True, host='0.0.0.0', port=port)
