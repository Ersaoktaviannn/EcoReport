import unittest
import json
from app import app, db, User, Report, Category, Comment
from werkzeug.security import generate_password_hash

class EcoReportTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test data
        self.create_test_data()
    
    def tearDown(self):
        """Tear down test fixtures"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_data(self):
        """Create test data"""
        # Create test user
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass'),
            full_name='Test User'
        )
        
        # Create admin user
        self.admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('adminpass'),
            full_name='Admin User',
            is_admin=True
        )
        
        # Create test category
        self.test_category = Category(
            name='Test Category',
            description='Test Description',
            icon='🧪'
        )
        
        db.session.add_all([self.test_user, self.admin_user, self.test_category])
        db.session.commit()
        
        # Create test report
        self.test_report = Report(
            title='Test Report',
            description='Test Description',
            location='Test Location',
            category_id=self.test_category.id,
            user_id=self.test_user.id,
            priority='medium'
        )
        
        db.session.add(self.test_report)
        db.session.commit()
    
    def login_user(self, username, password):
        """Helper method to login user"""
        return self.app.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def test_index_page(self):
        """Test dashboard page loads"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard Lingkungan', response.data)
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.app.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass',
            'full_name': 'New User'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        
        # Check user was created
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'new@example.com')
    
    def test_user_login(self):
        """Test user login"""
        response = self.login_user('testuser', 'testpass')
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_login(self):
        """Test invalid login"""
        response = self.login_user('testuser', 'wrongpass')
        self.assertIn(b'Username atau password salah', response.data)
    
    def test_create_report_authenticated(self):
        """Test creating report when authenticated"""
        self.login_user('testuser', 'testpass')
        
        response = self.app.post('/report/new', data={
            'title': 'New Test Report',
            'description': 'This is a test report description',
            'location': 'Test Location',
            'category_id': self.test_category.id,
            'priority': 'high'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Check report was created
        report = Report.query.filter_by(title='New Test Report').first()
        self.assertIsNotNone(report)
    
    def test_create_report_unauthenticated(self):
        """Test creating report when not authenticated"""
        response = self.app.post('/report/new', data={
            'title': 'Unauthorized Report',
            'description': 'This should not work',
            'location': 'Test Location',
            'category_id': self.test_category.id,
            'priority': 'high'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_view_report(self):
        """Test viewing report details"""
        response = self.app.get(f'/report/{self.test_report.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Report', response.data)
    
    def test_add_comment_authenticated(self):
        """Test adding comment when authenticated"""
        self.login_user('testuser', 'testpass')
        
        response = self.app.post(f'/report/{self.test_report.id}/comment', data={
            'content': 'This is a test comment'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after adding comment
        
        # Check comment was created
        comment = Comment.query.filter_by(content='This is a test comment').first()
        self.assertIsNotNone(comment)
    
    def test_admin_panel_access(self):
        """Test admin panel access"""
        # Test with admin user
        self.login_user('admin', 'adminpass')
        response = self.app.get('/admin/reports')
        self.assertEqual(response.status_code, 200)
        
        # Test with regular user
        self.login_user('testuser', 'testpass')
        response = self.app.get('/admin/reports')
        self.assertEqual(response.status_code, 302)  # Redirect due to no access
    
    def test_update_report_status_admin(self):
        """Test updating report status as admin"""
        self.login_user('admin', 'adminpass')
        
        response = self.app.post(f'/admin/report/{self.test_report.id}/update_status', data={
            'status': 'resolved'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Check status was updated
        updated_report = Report.query.get(self.test_report.id)
        self.assertEqual(updated_report.status, 'resolved')
    
    def test_api_get_reports(self):
        """Test API endpoint for getting reports"""
        response = self.app.get('/api/v1/reports')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('reports', data)
        self.assertIn('pagination', data)
    
    def test_api_get_categories(self):
        """Test API endpoint for getting categories"""
        response = self.app.get('/api/v1/categories')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_api_stats(self):
        """Test API statistics endpoint"""
        response = self.app.get('/api/v1/stats/summary')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('total_reports', data)
        self.assertIn('by_status', data)
        self.assertIn('by_category', data)

if __name__ == '__main__':
    unittest.main()