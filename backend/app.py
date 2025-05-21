# backend/app.py
from flask import Flask
from flask_cors import CORS
import config
from backend.extensions import cache

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    CORS(app)

    # init with ALL of config.py, including CACHE_REDIS_URL if set
    cache.init_app(app)

    from backend.api.data import bp as data_bp
    app.register_blueprint(data_bp, url_prefix="/api")

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
