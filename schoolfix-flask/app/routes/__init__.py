from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# Libera o acesso para qualquer origem (Netlify, localhost, etc.)
CORS(app, resources={r"/*": {"origins": "*"}})