from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.auth.decorators import admin_required


admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/cases')
@login_required
@admin_required
def manage_cases():
    return render_template('admin/cases.html')
