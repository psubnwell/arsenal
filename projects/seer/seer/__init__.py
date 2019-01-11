import os

from flask import Flask

from seer.blueprints.analysis import analysis_bp

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('seer')
    register_blueprints(app)
    return app

def register_blueprints(app):
    app.register_blueprint(analysis_bp)
