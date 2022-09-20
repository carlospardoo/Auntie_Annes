
from flask import Flask
from .server_test import test as default

ENDPOINTS = [('/', default)]

def create_app():
    app = Flask(__name__)

    for url, blueprint in ENDPOINTS:
        app.register_blueprint(blueprint, url_prefix = url)

    return app


if __name__ == '__main__':
    app = create_app(port = 5002)

    app.run()

