from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import jwt
from functools import wraps

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({'message': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        
        try:
            # Import models at runtime to avoid circular imports
            from app import db, Report, Category, User, Comment
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
            current_user = User.query.get(current_user_id)
        except:
            return jsonify({'message': 'Token invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Authentication Endpoints
@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """API Login endpoint"""
    from app import db, Report, Category, User, Comment
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'is_admin': user.is_admin
            }
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    """API Registration endpoint"""
    from app import db, Report, Category, User, Comment
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password', 'full_name']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data['full_name'],
        phone=data.get('phone', ''),
        password_hash=generate_password_hash(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

# Reports Endpoints
@api_bp.route('/reports', methods=['GET'])
def api_get_reports():
    """Get all reports with filtering"""
    from app import db, Report, Category, User, Comment
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
            'category': {
                'id': report.category.id,
                'name': report.category.name,
                'icon': report.category.icon
            },
            'reporter': {
                'id': report.reporter.id,
                'full_name': report.reporter.full_name
            }
        } for report in reports.items],
        'pagination': {
            'page': page,
            'pages': reports.pages,
            'per_page': per_page,
            'total': reports.total,
            'has_next': reports.has_next,
            'has_prev': reports.has_prev
        }
    })

@api_bp.route('/reports/<int:report_id>', methods=['GET'])
def api_get_report(report_id):
    """Get single report details"""
    from app import db, Report, Category, User, Comment
    report = Report.query.get_or_404(report_id)
    comments = Comment.query.filter_by(report_id=report_id).order_by(Comment.created_at.desc()).all()
    
    return jsonify({
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
        'category': {
            'id': report.category.id,
            'name': report.category.name,
            'description': report.category.description,
            'icon': report.category.icon
        },
        'reporter': {
            'id': report.reporter.id,
            'full_name': report.reporter.full_name,
            'email': report.reporter.email
        },
        'comments': [{
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'is_official': comment.is_official,
            'author': {
                'id': comment.author.id,
                'full_name': comment.author.full_name
            }
        } for comment in comments]
    })

@api_bp.route('/reports', methods=['POST'])
@token_required
def api_create_report(current_user):
    """Create new report"""
    from app import db, Report, Category, User, Comment
    data = request.get_json()
    
    required_fields = ['title', 'description', 'location', 'category_id', 'priority']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    report = Report(
        title=data['title'],
        description=data['description'],
        location=data['location'],
        category_id=data['category_id'],
        priority=data['priority'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        user_id=current_user.id
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({
        'message': 'Report created successfully',
        'report_id': report.id
    }), 201

@api_bp.route('/reports/<int:report_id>/comments', methods=['POST'])
@token_required
def api_add_comment(current_user, report_id):
    """Add comment to report"""
    from app import db, Report, Category, User, Comment
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'message': 'Comment content required'}), 400
    
    comment = Comment(
        content=data['content'],
        report_id=report_id,
        user_id=current_user.id,
        is_official=current_user.is_admin
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({'message': 'Comment added successfully'}), 201

# Categories Endpoints
@api_bp.route('/categories', methods=['GET'])
def api_get_categories():
    """Get all categories"""
    from app import db, Report, Category, User, Comment
    categories = Category.query.all()
    
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'description': cat.description,
        'icon': cat.icon
    } for cat in categories])

# Statistics Endpoints
@api_bp.route('/stats/summary', methods=['GET'])
def api_get_stats():
    """Get application statistics"""
    from app import db, Report, Category, User, Comment
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

# Admin Endpoints
@api_bp.route('/admin/reports/<int:report_id>/status', methods=['PUT'])
@token_required
def api_update_report_status(current_user, report_id):
    """Update report status (admin only)"""
    from app import db, Report, Category, User, Comment
    if not current_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data or not data.get('status'):
        return jsonify({'message': 'Status required'}), 400
    
    report = Report.query.get_or_404(report_id)
    report.status = data['status']
    report.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Status updated successfully'})