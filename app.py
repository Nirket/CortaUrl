from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/cortaurl.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(512), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)

def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.before_first_request
def create_tables():
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
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
