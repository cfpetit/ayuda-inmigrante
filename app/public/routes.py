import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, send_from_directory, abort, request
from flask_login import login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from app import db, mail
from app.models import Case, Document, JobPosting, NewsPost

public_bp = Blueprint('public', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@public_bp.route('/')
def index():
    recent_news = NewsPost.query.order_by(NewsPost.created_at.desc()).limit(3).all()
    recent_jobs = JobPosting.query.filter_by(is_active=True).order_by(JobPosting.created_at.desc()).limit(3).all()
    return render_template('public/index.html', recent_news=recent_news, recent_jobs=recent_jobs)

@public_bp.route('/services')
def services():
    return render_template('public/services.html')

# --- EMPLOYMENT AGENCY SECTION ---
@public_bp.route('/employment')
def employment():
    jobs = JobPosting.query.filter_by(is_active=True).order_by(JobPosting.created_at.desc()).all()
    return render_template('public/employment.html', jobs=jobs)

# --- NEWS & INTERVIEWS SECTION ---
@public_bp.route('/news')
def news_list():
    category = request.args.get('category')
    query = NewsPost.query
    if category in ['News', 'Interview']:
        query = query.filter_by(category=category)
    posts = query.order_by(NewsPost.created_at.desc()).all()
    return render_template('public/news.html', posts=posts, selected_category=category)

@public_bp.route('/news/<int:post_id>')
def news_detail(post_id):
    post = NewsPost.query.get_or_404(post_id)
    return render_template('public/news_detail.html', post=post)

@public_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('public/dashboard.html', user=current_user)

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

        file = request.files.get('document')
        if file and file.filename != '' and allowed_file(file.filename):
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

        # Send email notification to admin upon successful case creation
        try:
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@cylcae.com')
            sender = current_app.config.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME') or 'noreply@cylcae.es'
            
            msg = Message(
                subject=f"📋 New Application Submitted: #{new_case.id} ({new_case.case_type})",
                sender=sender,
                recipients=[admin_email],
                body=f"A new application has been submitted on the portal.\n\n"
                     f"Application ID: #{new_case.id}\n"
                     f"Applicant Email: {current_user.email}\n"
                     f"Type: {new_case.case_type}\n"
                     f"Context/Notes: {new_case.notes or 'None provided'}\n\n"
                     f"Review it in the admin dashboard."
            )
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email notification: {e}")

        flash('Application created successfully!', 'success')
        return redirect(url_for('public.case_detail', case_id=new_case.id))

    selected_type = request.args.get('type', '')
    return render_template('public/create_case.html', selected_type=selected_type)

@public_bp.route('/cases/<int:case_id>', methods=['GET', 'POST'])
@login_required
def case_detail(case_id):
    case = Case.query.get_or_404(case_id)
    if case.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        file = request.files.get('document')
        if file and allowed_file(file.filename):
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

    return render_template('public/case_detail.html', case=case)

@public_bp.route('/media/<filename>')
@login_required
def view_media(filename):
    doc = Document.query.filter_by(stored_filename=filename).first_or_404()
    if doc.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
