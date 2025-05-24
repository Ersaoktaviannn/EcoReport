import os
import json
from datetime import datetime, timedelta
from app import app, db, User, Category, Report, Comment
from werkzeug.security import generate_password_hash
import random

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if User.query.count() > 0:
            print("Database already initialized!")
            return
        
        print("Initializing database...")
        
        # Create categories
        categories_data = [
            {
                'name': 'Pencemaran Air',
                'description': 'Laporan terkait pencemaran sumber air, sungai, danau, dan laut',
                'icon': '💧'
            },
            {
                'name': 'Pencemaran Udara',
                'description': 'Laporan terkait polusi udara, asap kendaraan, dan industri',
                'icon': '🌫️'
            },
            {
                'name': 'Sampah Ilegal',
                'description': 'Pembuangan sampah sembarangan dan illegal dumping',
                'icon': '🗑️'
            },
            {
                'name': 'Kerusakan Hutan',
                'description': 'Penebangan liar, deforestasi, dan kerusakan hutan',
                'icon': '🌳'
            },
            {
                'name': 'Pencemaran Suara',
                'description': 'Polusi suara berlebihan dari kendaraan dan industri',
                'icon': '🔊'
            },
            {
                'name': 'Pencemaran Tanah',
                'description': 'Kontaminasi tanah oleh limbah industri dan kimia',
                'icon': '🏭'
            },
            {
                'name': 'Kerusakan Laut',
                'description': 'Pencemaran laut, kerusakan terumbu karang',
                'icon': '🌊'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            categories.append(category)
            db.session.add(category)
        
        # Create users
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@ecoreport.com',
                'password': 'admin123',
                'full_name': 'Administrator',
                'phone': '+62812345678',
                'is_admin': True
            },
            {
                'username': 'budi_santoso',
                'email': 'budi@gmail.com',
                'password': 'budi123',
                'full_name': 'Budi Santoso',
                'phone': '+628123456789'
            },
            {
                'username': 'siti_nurhaliza',
                'email': 'siti@yahoo.com',
                'password': 'siti123',
                'full_name': 'Siti Nurhaliza',
                'phone': '+628234567890'
            },
            {
                'username': 'ahmad_fauzi',
                'email': 'ahmad@outlook.com',
                'password': 'ahmad123',
                'full_name': 'Ahmad Fauzi',
                'phone': '+628345678901'
            },
            {
                'username': 'dewi_sartika',
                'email': 'dewi@gmail.com',
                'password': 'dewi123',
                'full_name': 'Dewi Sartika',
                'phone': '+628456789012'
            }
        ]
        
        users = []
        for user_data in users_data:
            password = user_data.pop('password')
            user = User(**user_data)
            user.password_hash = generate_password_hash(password)
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # Create sample reports
        sample_reports = [
            {
                'title': 'Pencemaran Sungai Ciliwung Jakarta',
                'description': 'Ditemukan limbah industri yang dibuang langsung ke Sungai Ciliwung di kawasan industri. Air sungai berubah warna menjadi kehitaman dan berbau tidak sedap. Ikan-ikan mulai mati dan masyarakat sekitar mengeluhkan bau yang menyengat.',
                'location': 'Jl. Industri Raya, Jakarta Timur',
                'latitude': -6.2297,
                'longitude': 106.9145,
                'priority': 'critical',
                'status': 'pending'
            },
            {
                'title': 'Penebangan Liar di Hutan Bogor',
                'description': 'Aktivitas penebangan liar ditemukan di kawasan hutan lindung Bogor. Pohon-pohon besar ditebang tanpa izin dan meninggalkan kerusakan ekosistem yang parah. Diperlukan tindakan segera untuk mencegah kerusakan lebih lanjut.',
                'location': 'Kawasan Hutan Lindung Bogor, Jawa Barat',
                'latitude': -6.5971,
                'longitude': 106.8060,
                'priority': 'high',
                'status': 'investigating'
            },
            {
                'title': 'Polusi Udara Berlebihan di Jalan Tol',
                'description': 'Asap kendaraan bermotor di ruas Jalan Tol Jagorawi sangat pekat, terutama pada jam sibuk. Visibilitas berkurang drastis dan mengganggu pernapasan pengendara. Perlu adanya monitoring kualitas udara dan pengaturan lalu lintas.',
                'location': 'Jalan Tol Jagorawi KM 15, Depok',
                'latitude': -6.3751,
                'longitude': 106.8650,
                'priority': 'medium',
                'status': 'pending'
            },
            {
                'title': 'Pembuangan Sampah Ilegal di Pinggir Jalan',
                'description': 'Tumpukan sampah besar ditemukan di pinggir Jalan Raya Bekasi. Sampah sudah menumpuk selama berminggu-minggu dan mulai menimbulkan bau busuk. Diperlukan pembersihan segera dan pengawasan agar tidak terulang.',
                'location': 'Jalan Raya Bekasi KM 8, Bekasi',
                'latitude': -6.2383,
                'longitude': 106.9756,
                'priority': 'medium',
                'status': 'resolved'
            },
            {
                'title': 'Kebisingan Pabrik Mengganggu Warga',
                'description': 'Pabrik tekstil di kawasan industri mengeluarkan suara bising hingga larut malam. Warga sekitar sulit tidur dan anak-anak terganggu belajarnya. Sudah ada laporan ke pihak berwenang tapi belum ada tindakan.',
                'location': 'Kawasan Industri Cibitung, Bekasi',
                'latitude': -6.2297,
                'longitude': 107.0185,
                'priority': 'medium',
                'status': 'investigating'
            },
            {
                'title': 'Kontaminasi Tanah oleh Limbah Kimia',
                'description': 'Tanah di sekitar pabrik kimia berubah warna dan tanaman tidak dapat tumbuh. Diduga terjadi kontaminasi akibat pembuangan limbah yang tidak sesuai prosedur. Perlu pengujian laboratorium dan pembersihan area.',
                'location': 'Jl. Kimia Industri, Tangerang',
                'latitude': -6.1781,
                'longitude': 106.6319,
                'priority': 'high',
                'status': 'pending'
            },
            {
                'title': 'Kerusakan Terumbu Karang Pulau Seribu',
                'description': 'Terumbu karang di Pulau Seribu mengalami pemutihan massal. Diduga akibat pemanasan global dan pencemaran laut. Ekosistem laut terganggu dan ikan-ikan mulai berkurang. Diperlukan program konservasi segera.',
                'location': 'Pulau Seribu, DKI Jakarta',
                'latitude': -5.6333,
                'longitude': 106.5167,
                'priority': 'critical',
                'status': 'investigating'
            }
        ]
        
        # Create reports with random assignments
        for i, report_data in enumerate(sample_reports):
            report_data['user_id'] = users[i % len(users)].id
            report_data['category_id'] = categories[i % len(categories)].id
            
            # Random date within last 30 days
            days_ago = random.randint(1, 30)
            report_data['created_at'] = datetime.utcnow() - timedelta(days=days_ago)
            
            if report_data['status'] != 'pending':
                report_data['updated_at'] = report_data['created_at'] + timedelta(
                    days=random.randint(1, 10)
                )
            
            report = Report(**report_data)
            db.session.add(report)
        
        db.session.commit()
        
        # Create sample comments
        reports = Report.query.all()
        for report in reports[:4]:  # Add comments to first 4 reports
            # User comment
            comment1 = Comment(
                content=f'Saya juga melihat kondisi ini di lokasi. Situasinya memang mengkhawatirkan dan perlu segera ditangani.',
                report_id=report.id,
                user_id=users[1].id,
                created_at=report.created_at + timedelta(hours=2)
            )
            
            # Official comment (admin)
            comment2 = Comment(
                content=f'Terima kasih atas laporan ini. Tim kami sedang melakukan investigasi lebih lanjut dan akan mengambil tindakan yang diperlukan.',
                report_id=report.id,
                user_id=users[0].id,  # admin
                is_official=True,
                created_at=report.created_at + timedelta(days=1)
            )
            
            db.session.add_all([comment1, comment2])
        
        db.session.commit()
        print("Database initialized successfully with sample data!")

def backup_database():
    """Backup database to JSON file"""
    with app.app_context():
        backup_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'users': [],
            'categories': [],
            'reports': [],
            'comments': []
        }
        
        # Backup users (without password)
        for user in User.query.all():
            backup_data['users'].append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat()
            })
        
        # Backup categories
        for category in Category.query.all():
            backup_data['categories'].append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'icon': category.icon
            })
        
        # Backup reports
        for report in Report.query.all():
            backup_data['reports'].append({
                'id': report.id,
                'title': report.title,
                'description': report.description,
                'location': report.location,
                'latitude': report.latitude,
                'longitude': report.longitude,
                'status': report.status,
                'priority': report.priority,
                'created_at': report.created_at.isoformat(),
                'updated_at': report.updated_at.isoformat(),
                'user_id': report.user_id,
                'category_id': report.category_id
            })
        
        # Backup comments
        for comment in Comment.query.all():
            backup_data['comments'].append({
                'id': comment.id,
                'content': comment.content,
                'created_at': comment.created_at.isoformat(),
                'is_official': comment.is_official,
                'report_id': comment.report_id,
                'user_id': comment.user_id
            })
        
        # Save to file
        filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"Database backup saved to {filename}")

def reset_database():
    """Reset database and reinitialize with fresh data"""
    with app.app_context():
        print("Resetting database...")
        db.drop_all()
        init_database()
        print("Database reset complete!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python db_utils.py [init|backup|reset]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_database()
    elif command == 'backup':
        backup_database()
    elif command == 'reset':
        reset_database()
    else:
        print("Unknown command. Use: init, backup, or reset")