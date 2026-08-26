import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Case, JobPosting, NewsPost
import cloudinary.uploader

admin_bp = Blueprint('admin', __name__, template_folder='templates')

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access restricted to administrators.", "danger")
            return redirect(url_for('public.index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    cases = Case.query.order_by(Case.created_at.desc()).all()
    jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).all()
    posts = NewsPost.query.order_by(NewsPost.created_at.desc()).all()
    return render_template('admin/dashboard.html', cases=cases, jobs=jobs, posts=posts)

# --- CASE MANAGEMENT ROUTES ---

@admin_bp.route('/cases/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def review_case(id):
    case = Case.query.get_or_404(id)
    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status:
            case.status = new_status
            db.session.commit()
            flash(f"Case #{case.id} status updated to '{new_status}'.", "success")
        return redirect(url_for('admin.review_case', id=case.id))

    return render_template('public/case_detail.html', case=case)

# --- JOB POSTING ROUTES ---

@admin_bp.route('/jobs/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_job():
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        location = request.form.get('location')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        
        file_url = None
        if 'attachment' in request.files and request.files['attachment'].filename:
            upload_result = cloudinary.uploader.upload(
                request.files['attachment'], 
                resource_type="auto", 
                folder="cylcae_jobs"
            )
            file_url = upload_result.get('secure_url')

        job = JobPosting(
            title=title,
            company=company,
            location=location,
            description=description,
            requirements=requirements,
            file_url=file_url
        )
        db.session.add(job)
        db.session.commit()
        flash("Job posting created successfully!", "success")
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/job_form.html', job=None)

@admin_bp.route('/jobs/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_job(id):
    job = JobPosting.query.get_or_404(id)
    if request.method == 'POST':
        job.title = request.form.get('title')
        job.company = request.form.get('company')
        job.location = request.form.get('location')
        job.description = request.form.get('description')
        job.requirements = request.form.get('requirements')
        job.is_active = 'is_active' in request.form

        if 'attachment' in request.files and request.files['attachment'].filename:
            upload_result = cloudinary.uploader.upload(
                request.files['attachment'], 
                resource_type="auto", 
                folder="cylcae_jobs"
            )
            job.file_url = upload_result.get('secure_url')

        db.session.commit()
        flash("Job posting updated successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/job_form.html', job=job)

@admin_bp.route('/jobs/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_job(id):
    job = JobPosting.query.get_or_404(id)
    db.session.delete(job)
    db.session.commit()
    flash("Job posting deleted.", "info")
    return redirect(url_for('admin.dashboard'))

# --- NEWS & INTERVIEWS ROUTES ---

@admin_bp.route('/news/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_news():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        content = request.form.get('content')
        
        image_url = None
        if 'image' in request.files and request.files['image'].filename:
            img_result = cloudinary.uploader.upload(
                request.files['image'], 
                folder="cylcae_news_images"
            )
            image_url = img_result.get('secure_url')

        file_url = None
        if 'document' in request.files and request.files['document'].filename:
            doc_result = cloudinary.uploader.upload(
                request.files['document'], 
                resource_type="auto", 
                folder="cylcae_news_docs"
            )
            file_url = doc_result.get('secure_url')

        post = NewsPost(
            title=title,
            category=category,
            content=content,
            image_url=image_url,
            file_url=file_url
        )
        db.session.add(post)
        db.session.commit()
        flash("News post created successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/news_form.html', post=None)

@admin_bp.route('/news/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_news(id):
    post = NewsPost.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.category = request.form.get('category')
        post.content = request.form.get('content')

        if 'image' in request.files and request.files['image'].filename:
            img_result = cloudinary.uploader.upload(
                request.files['image'], 
                folder="cylcae_news_images"
            )
            post.image_url = img_result.get('secure_url')

        if 'document' in request.files and request.files['document'].filename:
            doc_result = cloudinary.uploader.upload(
                request.files['document'], 
                resource_type="auto", 
                folder="cylcae_news_docs"
            )
            post.file_url = doc_result.get('secure_url')

        db.session.commit()
        flash("News post updated successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/news_form.html', post=post)

@admin_bp.route('/news/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_news(id):
    post = NewsPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash("News post deleted.", "info")
    return redirect(url_for('admin.dashboard'))
