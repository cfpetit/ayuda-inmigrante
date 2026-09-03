from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_babel import get_locale
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cases = db.relationship('Case', backref='applicant', lazy=True)
    documents = db.relationship('Document', backref='uploader', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    case_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Pending Review')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    documents = db.relationship('Document', backref='case', lazy=True, cascade="all, delete-orphan")
    admin_notes = db.Column(db.Text, nullable=True)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stored_filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- NEW SECTIONS ---

class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(150), nullable=True)
    location = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(500), nullable=True)  # Cloudinary file/doc URL
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def title(self):
        if str(get_locale()) == 'es' and self.title_es:
            return self.title_es
        return self.title_en

    @property
    def description(self):
        if str(get_locale()) == 'es' and self.description_es:
            return self.description_es
        return self.description_en

    @property
    def requirements(self):
        if str(get_locale()) == 'es' and self.requirements_es:
            return self.requirements_es
        return self.requirements_en

class NewsPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='News')  # 'News' or 'Interview'
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)  # Cloudinary image URL
    file_url = db.Column(db.String(500), nullable=True)   # Cloudinary PDF/attachment URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def title(self):
        if str(get_locale()) == 'es' and self.title_es:
            return self.title_es
        return self.title_en

    @property
    def content(self):
        if str(get_locale()) == 'es' and self.content_es:
            return self.content_es
        return self.content_es

class PropertyListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    listing_type = db.Column(db.String(50), nullable=False)   # 'Sale', 'Lease', 'Business'
    property_type = db.Column(db.String(50), nullable=False)  # 'House', 'Apartment', 'Commercial Space', 'Land'
    price = db.Column(db.Float, nullable=False)
    price_period = db.Column(db.String(20), default='Total')  # 'Total', '/month', '/year'
    location = db.Column(db.String(200), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=True)
    bathrooms = db.Column(db.Integer, nullable=True)
    area_sqm = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)     # Cloudinary image URL
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def title(self):
        if str(get_locale()) == 'es' and self.title_es:
            return self.title_es
        return self.content_es

    @property
    def description(self):
        if str(get_locale()) == 'es' and self.description_es:
            return self.description_es
        return self.description_en

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

