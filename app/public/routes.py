import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, send_from_directory, abort, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Case, Document

public_bp = Blueprint('public', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@public_bp.route('/')
def index():
    return render_template('public/index.html')

@public_bp.route('/services')
def services():
    return render_template('public/services.html')

@public_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('public/dasboard.html', user=current_user)

@public_bp.route('/quiz')
def quiz():
    return render_template('public/quiz.html')

@public_bp.route('/cases/new', methods=['GET', 'POST'])
@login_required
def create_case():
    if request.method == 'POST':
        case_type = request.form.get('case_type')
        notes = request.form.get('notes')

        if not case_type:
            flash('Please select a valid application type.', 'error')
            return redirect(url_for('public.create_case'))

        new_case = Case(case_type=case_type, notes=notes, applicant=current_user)
        db.session.add(new_case)
        db.session.commit()

        # Handle optional initial file upload
        file = request.files.get('document')
        if file and file.filename != '':
            if allowed_file(file.filename):
                orig_filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{orig_filename}"

                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(upload_path)

                doc = Document(
                    stored_filename=unique_filename,
                    original_filename=orig_filename,
                    case_id=new_case.id,
                    user_id=current_user.id
                )
                db.session.add(doc)
                db.session.commit()
            else:
                flash('Application created, but file extension is not allowed (PDF, PNG, JPG, DOC, DOCX only).', 'warning')

        flash('Immigration case submitted successfully!', 'success')
        return redirect(url_for('public.case_detail', case_id=new_case.id))
    selected_type = request.args.get('type', '')
    return render_template('public/create_case.html', selected_type=selected_type)

@public_bp.route('/cases/<int:case_id>', methods=['GET', 'POST'])
@login_required
def case_detail(case_id):
    case = Case.query.get_or_404(case_id)

    # Ensure user owns this case (or is an admin)
    if case.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        file = request.files.get('document')
        if file and file.filename != '' and allowed_file(file.filename):
            orig_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{orig_filename}"

            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(upload_path)

            doc = Document(
                stored_filename=unique_filename,
                original_filename=orig_filename,
                case_id=case.id,
                user_id=current_user.id
            )
            db.session.add(doc)
            db.session.commit()
            flash('Document uploaded successfully!', 'success')
            return redirect(url_for('public.case_detail', case_id=case.id))
        else:
            flash('Invalid file format. Allowed: PDF, PNG, JPG, DOC, DOCX.', 'error')

    return render_template('public/case_detail.html', case=case)


@public_bp.route('/media/<filename>')
@login_required
def view_media(filename):
    doc = Document.query.filter_by(stored_filename=filename).first_or_404()

    if doc.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


