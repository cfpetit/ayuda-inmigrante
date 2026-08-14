from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required
from flask_mail import Message
from app.auth.decorators import admin_required
from app.models import Case, Document, User
from app import db, mail


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

@admin_bp.route('/cases/<int:case_id>/review', methods=['GET', 'POST'])
@login_required
@admin_required
def review_case(case_id):
    if not current_user.is_admin:
        abort(403)

    case = Case.query.get_or_404(case_id)
    applicant = User.query.get_or_404(case.user_id)

    if request.method == 'POST':
        new_status = request.form.get('status')
        admin_notes = request.form.get('notes')

        status_changed = (case_status != new_status)

        case.status = new_status
        case.notes = admin_notes
        db.session.commit()

        if status_changed:
            try:
                msg = Message(subject=f"Inmigration portal: Update on case #{case.id}", recipients=[applicant.email])
                msg.body = f"""Hello, There has been an update to your immigration application (Case #{case.id} - {case.case_type}).
New Status: {case.status}

Administrator Notes:
{case.notes if case.notes else 'No additional notes provided.'}

Please log in to your dashboard to view further details.

Regards,
Immigration Portal Team
"""
                mail.send(msg)
                flash(f'Case updated and email sent to applicant.', 'success')
            except Exception as e:
                flash(f'Case updated but failed to send email: {str(e)}', 'warning')
        else:
            flash('Case updated succesfully (No status change, so no email sent).', 'success')
        return redirect(url_for('admin.review_case', case_id=case.id))
    return render_template('admin/case_detail.html', case=case)
