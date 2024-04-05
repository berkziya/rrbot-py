from flask import Blueprint, render_template, current_app

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    user = current_app.config['USER']
    return render_template('profile.html', user=user)

@bp.route('/moe')
def moe():
    user = current_app.config['USER']
    return render_template('moe.html', user=user)
