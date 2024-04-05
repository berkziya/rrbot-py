from flask import Flask

def create_app(user):
    app = Flask(__name__)
    app.config['USER'] = user
    
    from .routes import bp
    app.register_blueprint(bp)
    return app