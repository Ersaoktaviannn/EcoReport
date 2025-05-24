# app.py - Main Flask Application

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///environmental_reports.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models (4+ Entitas sesuai requirement)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationship
    reports = db.relationship('Report', backref='reporter', lazy=True)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    
    # Relationship
    reports = db.relationship('Report', backref='category', lazy=True)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, investigating, resolved
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Relationship
    comments = db.relationship('Comment', backref='report', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_official = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship
    author = db.relationship('User', backref='comments')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register API Blueprint
from api import api_bp
app.register_blueprint(api_bp)

# Web Routes

@app.route('/')
def index():
    """Dashboard utama dengan statistik"""
    total_reports = Report.query.count()
    pending_reports = Report.query.filter_by(status='pending').count()
    resolved_reports = Report.query.filter_by(status='resolved').count()
    
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(5).all()
    categories = Category.query.all()
    
    # Statistik per kategori
    category_stats = []
    for cat in categories:
        count = Report.query.filter_by(category_id=cat.id).count()
        category_stats.append({'name': cat.name, 'count': count})
    
    return render_template('dashboard.html', 
                         total_reports=total_reports,
                         pending_reports=pending_reports,
                         resolved_reports=resolved_reports,
                         recent_reports=recent_reports,
                         category_stats=category_stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form.get('phone', '')
        
        # Validasi
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan!')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar!')
            return redirect(url_for('register'))
        
        # Buat user baru
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            phone=phone
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah!')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/report/new', methods=['GET', 'POST'])
@login_required
def new_report():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        category_id = request.form['category_id']
        priority = request.form['priority']
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        report = Report(
            title=title,
            description=description,
            location=location,
            category_id=category_id,
            priority=priority,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            user_id=current_user.id
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Laporan berhasil dikirim!')
        return redirect(url_for('view_report', id=report.id))
    
    categories = Category.query.all()
    return render_template('new_report.html', categories=categories)

@app.route('/reports')
def reports():
    """Daftar semua laporan dengan filter"""
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    
    query = Report.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if category_filter != 'all':
        query = query.filter_by(category_id=category_filter)
    
    reports = query.order_by(Report.created_at.desc()).all()
    categories = Category.query.all()
    
    return render_template('reports.html', 
                         reports=reports, 
                         categories=categories,
                         current_status=status_filter,
                         current_category=category_filter)

@app.route('/report/<int:id>')
def view_report(id):
    """Detail laporan"""
    report = Report.query.get_or_404(id)
    comments = Comment.query.filter_by(report_id=id).order_by(Comment.created_at.desc()).all()
    return render_template('view_report.html', report=report, comments=comments)

@app.route('/report/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    content = request.form['content']
    
    comment = Comment(
        content=content,
        report_id=id,
        user_id=current_user.id,
        is_official=current_user.is_admin
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Komentar berhasil ditambahkan!')
    return redirect(url_for('view_report', id=id))

@app.route('/admin/reports')
@login_required
def admin_reports():
    """Panel admin untuk mengelola laporan"""
    if not current_user.is_admin:
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('admin_reports.html', reports=reports)

@app.route('/admin/report/<int:id>/update_status', methods=['POST'])
@login_required
def update_report_status(id):
    """Update status laporan (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    report = Report.query.get_or_404(id)
    new_status = request.form['status']
    
    report.status = new_status
    report.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Status laporan berhasil diubah menjadi {new_status}!')
    return redirect(url_for('admin_reports'))

# Compatibility API Endpoints for Tests
# These endpoints provide backward compatibility for existing tests

@app.route('/api/categories')
def api_get_categories():
    """Compatibility endpoint for categories"""
    categories = Category.query.all()
    result = []
    for c in categories:
        result.append({
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'icon': c.icon
        })
    return jsonify(result)

@app.route('/api/reports')
def api_get_reports():
    """Compatibility endpoint for reports with pagination wrapper"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)
    
    query = Report.query
    
    if status:
        query = query.filter_by(status=status)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    reports = query.order_by(Report.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'reports': [{
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'location': r.location,
            'latitude': r.latitude,
            'longitude': r.longitude,
            'status': r.status,
            'priority': r.priority,
            'created_at': r.created_at.isoformat(),
            'updated_at': r.updated_at.isoformat(),
            'category': {
                'id': r.category.id,
                'name': r.category.name,
                'icon': r.category.icon
            },
            'reporter': {
                'id': r.reporter.id,
                'username': r.reporter.username,
                'full_name': r.reporter.full_name
            }
        } for r in reports.items],
        'pagination': {
            'page': page,
            'pages': reports.pages,
            'per_page': per_page,
            'total': reports.total,
            'has_next': reports.has_next,
            'has_prev': reports.has_prev
        }
    })

@app.route('/api/stats/summary')
def api_reports_stats():
    """Compatibility endpoint for stats"""
    total_reports = Report.query.count()
    total_users = User.query.count()
    
    stats_by_status = {
        'pending': Report.query.filter_by(status='pending').count(),
        'investigating': Report.query.filter_by(status='investigating').count(),
        'resolved': Report.query.filter_by(status='resolved').count()
    }
    
    stats_by_priority = {
        'low': Report.query.filter_by(priority='low').count(),
        'medium': Report.query.filter_by(priority='medium').count(),
        'high': Report.query.filter_by(priority='high').count(),
        'critical': Report.query.filter_by(priority='critical').count()
    }
    
    categories_with_counts = []
    for category in Category.query.all():
        count = Report.query.filter_by(category_id=category.id).count()
        categories_with_counts.append({
            'id': category.id,
            'name': category.name,
            'icon': category.icon,
            'count': count
        })
    
    return jsonify({
        'total_reports': total_reports,
        'total_users': total_users,
        'by_status': stats_by_status,
        'by_priority': stats_by_priority,
        'by_category': categories_with_counts
    })

def init_db():
    """Inisialisasi database dengan data sample"""
    db.create_all()
    
    # Cek apakah sudah ada data
    if Category.query.count() == 0:
        # Tambah kategori
        categories = [
            Category(name='Pencemaran Air', description='Laporan terkait pencemaran sumber air', icon='💧'),
            Category(name='Pencemaran Udara', description='Laporan terkait polusi udara', icon='🌫️'),
            Category(name='Sampah Ilegal', description='Pembuangan sampah sembarangan', icon='🗑️'),
            Category(name='Kerusakan Hutan', description='Penebangan liar dan kerusakan hutan', icon='🌳'),
            Category(name='Pencemaran Suara', description='Polusi suara berlebihan', icon='🔊')
        ]
        
        for cat in categories:
            db.session.add(cat)
        
        # Tambah admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            full_name='Administrator',
            is_admin=True
        )
        db.session.add(admin)
        
        db.session.commit()
        print("Database initialized with sample data!")

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)