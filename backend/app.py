import sys
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent))

import config
from routes import auth_bp, config_bp, health_bp, audit_bp, users_bp

def create_app():
    app = Flask(__name__)

    CORS(app, resources={
        r"/api/*": {
            "origins": config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Registrar blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(users_bp)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'message': 'Rota não encontrada'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'success': False, 'message': 'Método não permitido'}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

    @app.route('/')
    def index():
        return jsonify({
            'status': 'online',
            'message': 'API de Reconhecimento Facial',
            'version': '2.0'
        })

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
