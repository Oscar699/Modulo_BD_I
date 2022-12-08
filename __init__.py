from flask import Flask
from conf.config import DevelopmentConfig
from app.api.view_api import api_bp
from app.views import public_bp

ACTIVE_ENDPOINTS = [('/api',api_bp), ('/',public_bp)]


def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    
    app.config.from_object(config)

    # register each active blueprint
    for url, blueprint in ACTIVE_ENDPOINTS:
        app.register_blueprint(blueprint, url_prefix=url)

    return app


if __name__ == "__main__":
    app_flask = create_app()
    app_flask.run(debug=True)