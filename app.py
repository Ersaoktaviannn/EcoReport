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
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

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

# Web Routes

@app.route('/')
def index():
    """Dashboard utama dengan statistik"""
    try:
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
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', 
                             total_reports=0,
                             pending_reports=0,
                             resolved_reports=0,
                             recent_reports=[],
                             category_stats=[])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            full_name = request.form['full_name']
            phone = request.form.get('phone', '')
            
            # Validasi
            if User.query.filter_by(username=username).first():
                flash('Username sudah digunakan!', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email sudah terdaftar!', 'error')
                return redirect(url_for('register'))
            
            # Buat user baru
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                phone=phone
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                flash(f'Selamat datang, {user.full_name}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Username atau password salah!', 'error')
        except Exception as e:
            flash(f'Error during login: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/report/new', methods=['GET', 'POST'])
@login_required
def new_report():
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            location = request.form['location']
            category_id = request.form['category_id']
            priority = request.form['priority']
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            
            # Validasi
            if not title or not description or not location:
                flash('Semua field wajib harus diisi!', 'error')
                return redirect(url_for('new_report'))
            
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
            
            flash('Laporan berhasil dikirim!', 'success')
            return redirect(url_for('view_report', id=report.id))
        except Exception as e:
            flash(f'Error creating report: {str(e)}', 'error')
            return redirect(url_for('new_report'))
    
    categories = Category.query.all()
    return render_template('new_report.html', categories=categories)

@app.route('/reports')
def reports():
    """Daftar semua laporan dengan filter"""
    try:
        status_filter = request.args.get('status', 'all')
        category_filter = request.args.get('category', 'all')
        
        query = Report.query
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        if category_filter != 'all':
            try:
                category_id = int(category_filter)
                query = query.filter_by(category_id=category_id)
            except ValueError:
                pass  # Invalid category_id, ignore filter
        
        reports = query.order_by(Report.created_at.desc()).all()
        categories = Category.query.all()
        
        return render_template('reports.html', 
                             reports=reports, 
                             categories=categories,
                             current_status=status_filter,
                             current_category=category_filter)
    except Exception as e:
        flash(f'Error loading reports: {str(e)}', 'error')
        return render_template('reports.html', 
                             reports=[], 
                             categories=[],
                             current_status='all',
                             current_category='all')

@app.route('/report/<int:id>')
def view_report(id):
    """Detail laporan"""
    try:
        report = Report.query.get_or_404(id)
        comments = Comment.query.filter_by(report_id=id).order_by(Comment.created_at.desc()).all()
        return render_template('view_report.html', report=report, comments=comments)
    except Exception as e:
        flash(f'Error loading report: {str(e)}', 'error')
        return redirect(url_for('reports'))

@app.route('/report/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    try:
        report = Report.query.get_or_404(id)
        content = request.form.get('content', '').strip()
        
        if not content:
            flash('Komentar tidak boleh kosong!', 'error')
            return redirect(url_for('view_report', id=id))
        
        comment = Comment(
            content=content,
            report_id=id,
            user_id=current_user.id,
            is_official=current_user.is_admin
        )
        
        db.session.add(comment)
        db.session.commit()
        
        flash('Komentar berhasil ditambahkan!', 'success')
    except Exception as e:
        flash(f'Error adding comment: {str(e)}', 'error')
    
    return redirect(url_for('view_report', id=id))

@app.route('/admin/reports')
@login_required
def admin_reports():
    """Panel admin untuk mengelola laporan"""
    if not current_user.is_admin:
        flash('Akses ditolak! Admin only.', 'error')
        return redirect(url_for('index'))
    
    try:
        reports = Report.query.order_by(Report.created_at.desc()).all()
        return render_template('admin_reports.html', reports=reports)
    except Exception as e:
        flash(f'Error loading admin panel: {str(e)}', 'error')
        return render_template('admin_reports.html', reports=[])

@app.route('/admin/report/<int:id>/update_status', methods=['POST'])
@login_required
def update_report_status(id):
    """Update status laporan (admin only)"""
    if not current_user.is_admin:
        flash('Akses ditolak! Admin only.', 'error')
        return redirect(url_for('view_report', id=id))
    
    try:
        report = Report.query.get_or_404(id)
        new_status = request.form.get('status')
        
        if new_status in ['pending', 'investigating', 'resolved']:
            old_status = report.status
            report.status = new_status
            report.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash(f'Status laporan berhasil diubah dari "{old_status}" ke "{new_status}"!', 'success')
        else:
            flash('Status tidak valid!', 'error')
    except Exception as e:
        flash(f'Error updating status: {str(e)}', 'error')
    
    return redirect(url_for('view_report', id=id))

# API Endpoints

@app.route('/api/categories')
def api_get_categories():
    """API endpoint untuk mendapatkan daftar kategori"""
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports')
def api_get_reports():
    """API endpoint untuk mendapatkan daftar laporan dengan pagination"""
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/summary')
def api_reports_stats():
    """API endpoint untuk statistik laporan"""
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/stats')
def api_reports_stats_alt():
    """Alternative stats endpoint for frontend compatibility"""
    try:
        by_status = {
            'pending': Report.query.filter_by(status='pending').count(),
            'investigating': Report.query.filter_by(status='investigating').count(),
            'resolved': Report.query.filter_by(status='resolved').count()
        }
        
        by_category = []
        for category in Category.query.all():
            count = Report.query.filter_by(category_id=category.id).count()
            by_category.append({
                'name': category.name,
                'count': count,
                'icon': category.icon
            })
        
        return jsonify({
            'by_status': by_status,
            'by_category': by_category,
            'total': Report.query.count()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error Handlers

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

def init_db():
    """Inisialisasi database dengan data sample yang lengkap"""
    db.create_all()
    
    # Cek apakah sudah ada data
    if Category.query.count() == 0:
        print("Initializing database with sample data...")
        
        try:
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
            
            # Tambah users (admin dan user biasa)
            admin = User(
                username='admin',
                email='admin@ecoreport.com',
                full_name='Administrator',
                phone='081234567890',
                is_admin=True
            )
            admin.set_password('admin')
            
            user1 = User(
                username='john_doe',
                email='john@example.com',
                full_name='John Doe',
                phone='081111111111',
                is_admin=False
            )
            user1.set_password('password')
            
            user2 = User(
                username='jane_smith',
                email='jane@example.com',
                full_name='Jane Smith',
                phone='081222222222',
                is_admin=False
            )
            user2.set_password('password')
            
            db.session.add(admin)
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()  # Commit untuk mendapatkan user IDs
            
            # Tambah sample reports
            sample_reports = [
                {
                    'title': 'Pencemaran Sungai Ciliwung Jakarta',
                    'description': 'Air sungai berubah warna menjadi kecoklatan dan berbau menyengat. Diduga ada limbah pabrik yang dibuang ke sungai. Banyak ikan mati mengapung di permukaan air.',
                    'location': 'Jl. Ciliwung Raya, Jakarta Timur',
                    'latitude': -6.2088,
                    'longitude': 106.8456,
                    'category_name': 'Pencemaran Air',
                    'priority': 'critical',
                    'status': 'investigating',
                    'user_id': user1.id
                },
                {
                    'title': 'Tumpukan Sampah di Taman Menteng',
                    'description': 'Sampah menumpuk di area taman selama 1 minggu tanpa dibersihkan. Menimbulkan bau tidak sedap dan menarik lalat serta hama lainnya. Anak-anak tidak bisa bermain dengan nyaman.',
                    'location': 'Taman Menteng, Jakarta Pusat',
                    'latitude': -6.1944,
                    'longitude': 106.8294,
                    'category_name': 'Sampah Ilegal',
                    'priority': 'high',
                    'status': 'pending',
                    'user_id': user2.id
                },
                {
                    'title': 'Asap Tebal dari Pabrik Tekstil',
                    'description': 'Pabrik tekstil mengeluarkan asap hitam tebal setiap hari, terutama saat malam hari. Warga sekitar mengeluh sesak napas dan mata perih.',
                    'location': 'Kawasan Industri Pulogadung, Jakarta Timur',
                    'latitude': -6.1789,
                    'longitude': 106.8842,
                    'category_name': 'Pencemaran Udara',
                    'priority': 'high',
                    'status': 'investigating',
                    'user_id': user1.id
                },
                {
                    'title': 'Penebangan Pohon Tanpa Izin',
                    'description': 'Aktivitas penebangan pohon besar-besaran tanpa izin di kawasan hijau. Diperkirakan lebih dari 30 pohon besar sudah ditebang dalam seminggu terakhir.',
                    'location': 'Hutan Kota Srengseng, Jakarta Barat',
                    'latitude': -6.1580,
                    'longitude': 106.7537,
                    'category_name': 'Kerusakan Hutan',
                    'priority': 'medium',
                    'status': 'resolved',
                    'user_id': user2.id
                },
                {
                    'title': 'Suara Bising Pabrik 24 Jam',
                    'description': 'Pabrik pengolahan logam beroperasi 24 jam dengan suara mesin yang sangat keras. Warga tidak bisa tidur dengan tenang, terutama yang tinggal di sekitar pabrik.',
                    'location': 'Kawasan Industri Cakung, Jakarta Timur',
                    'latitude': -6.1751,
                    'longitude': 106.9345,
                    'category_name': 'Pencemaran Suara',
                    'priority': 'medium',
                    'status': 'pending',
                    'user_id': user1.id
                },
                {
                    'title': 'Air PDAM Keruh dan Berbau',
                    'description': 'Air PDAM di kompleks perumahan keruh dan berbau aneh sejak 3 hari lalu. Warga terpaksa membeli air kemasan untuk kebutuhan sehari-hari.',
                    'location': 'Villa Indah, Bekasi',
                    'latitude': -6.2441,
                    'longitude': 107.0048,
                    'category_name': 'Pencemaran Air',
                    'priority': 'high',
                    'status': 'investigating',
                    'user_id': user2.id
                },
                {
                    'title': 'Pembuangan Sampah Liar di Kali',
                    'description': 'Warga masih membuang sampah sembarangan ke kali kecil di belakang perumahan. Kali menjadi mampet dan menimbulkan banjir saat hujan deras.',
                    'location': 'Kelurahan Cempaka Putih, Jakarta Pusat',
                    'latitude': -6.1653,
                    'longitude': 106.8650,
                    'category_name': 'Sampah Ilegal',
                    'priority': 'medium',
                    'status': 'pending',
                    'user_id': user1.id
                },
                {
                    'title': 'Kebocoran Pipa Air Bersih Besar',
                    'description': 'Pipa air bersih utama bocor besar di Jl. Sudirman. Air terbuang sia-sia dalam jumlah sangat besar sudah sejak 1 minggu yang lalu.',
                    'location': 'Jl. Sudirman, Jakarta Pusat',
                    'latitude': -6.2088,
                    'longitude': 106.8228,
                    'category_name': 'Pencemaran Air',
                    'priority': 'medium',
                    'status': 'resolved',
                    'user_id': user2.id
                }
            ]
            
            for report_data in sample_reports:
                category = Category.query.filter_by(name=report_data['category_name']).first()
                if category:
                    report = Report(
                        title=report_data['title'],
                        description=report_data['description'],
                        location=report_data['location'],
                        latitude=report_data.get('latitude'),
                        longitude=report_data.get('longitude'),
                        category_id=category.id,
                        priority=report_data['priority'],
                        status=report_data['status'],
                        user_id=report_data['user_id'],
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(report)
            
            # Tambah sample comments untuk beberapa laporan
            db.session.commit()  # Commit reports dulu
            
            reports = Report.query.all()
            if reports:
                # Comment untuk laporan pertama
                comment1 = Comment(
                    content="Tim sudah turun ke lokasi untuk investigasi. Akan segera diambil sampel air untuk analisis laboratorium.",
                    report_id=reports[0].id,
                    user_id=admin.id,
                    is_official=True
                )
                
                comment2 = Comment(
                    content="Terima kasih atas laporannya. Kondisi memang sangat memprihatinkan.",
                    report_id=reports[0].id,
                    user_id=user2.id,
                    is_official=False
                )
                
                db.session.add(comment1)
                db.session.add(comment2)
            
            db.session.commit()
            print("Database initialized successfully!")
            print("\n" + "="*50)
            print("LOGIN CREDENTIALS:")
            print("="*50)
            print("🔑 Admin Login:")
            print("   Username: admin")
            print("   Password: admin")
            print("\n👤 User Login:")
            print("   Username: john_doe")
            print("   Password: password")
            print("\n👤 User Login:")
            print("   Username: jane_smith") 
            print("   Password: password")
            print("="*50)
            
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()
    else:
        print("Database already initialized.")

if __name__ == '__main__':
    with app.app_context():
        init_db()
    print("\n🚀 Starting EcoReport Application...")
    print("📍 Access the application at: http://localhost:5000")
    app.run(debug=True)