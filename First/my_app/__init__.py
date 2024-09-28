from flask import Flask
from my_app.hello_as_bp.handlers import hello


app = Flask(__name__)
app.register_blueprint(hello)