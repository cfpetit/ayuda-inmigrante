from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.auth.decorators import admin_required
from app.models import Case, Document, User
from app import db


admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    cases = Case.query.order_by(Case.created_at.desc()).all()

    total_cases = len(cases)
    pending_cases = sum(1 for c in cases if c.status == 'Pending Review')
    approved_cases = sum(1 for c in cases if c.status == 'Approved')
    return render_template('admin/dashboard.html', cases=cases, total_cases=total_cases, pending_cases=pending_cases, approved_cases=approved_cases)

@admin_bp.route('/cases/<int:case_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def review_case(case_id):
    case = Case.query.get_or_404(case_id)

    if request.method == 'POST':
        new_status = request.form.get('status')
        admin_notes = request.form.get('notes')

        if new_status:
            case.status = new_status
        if admin_notes is not None:
            case.notes = admin_notes

        db.session.commit()
        flash(f'Case #{case.id} updated successfully!', 'success')
        return redirect(url_for('admin.review_case', case_id=case.id))
    return render_template('admin/case_detail.html', case=case)
