from flask import Flask
from flask_migrate import Migrate

from .config import Config
from .models import db
from .routes.api_keys import api_keys_bp
from .routes.documents import documents_bp
from .routes.projects import projects_bp

migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(projects_bp)
    app.register_blueprint(api_keys_bp)
    app.register_blueprint(documents_bp)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5002, debug=True)
