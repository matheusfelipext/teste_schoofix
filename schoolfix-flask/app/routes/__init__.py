from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# Permite requisições de qualquer origem, incluindo a checagem OPTIONS (preflight)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)