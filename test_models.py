import unittest
from app import app, db, User, Report, Category, Comment
from werkzeug.security import generate_password_hash, check_password_hash

class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_creation(self):
        """Test user model creation"""
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass'),
            full_name='Test User'
        )
        db.session.add(user)
        db.session.commit()
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(check_password_hash(user.password_hash, 'testpass'))
    
    def test_category_creation(self):
        """Test category model creation"""
        category = Category(
            name='Test Category',
            description='Test Description',
            icon='🧪'
        )
        db.session.add(category)
        db.session.commit()
        
        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, 'Test Category')
    
    def test_report_creation(self):
        """Test report model creation and relationships"""
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass'),
            full_name='Test User'
        )
        
        category = Category(
            name='Test Category',
            description='Test Description',
            icon='🧪'
        )
        
        db.session.add_all([user, category])
        db.session.commit()
        
        report = Report(
            title='Test Report',
            description='Test Description',
            location='Test Location',
            category_id=category.id,
            user_id=user.id
        )
        
        db.session.add(report)
        db.session.commit()
        
        self.assertIsNotNone(report.id)
        self.assertEqual(report.reporter, user)
        self.assertEqual(report.category, category)
    
    def test_comment_creation(self):
        """Test comment model creation and relationships"""
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass'),
            full_name='Test User'
        )
        
        category = Category(name='Test Category', icon='🧪')

        db.session.add_all([user, category])
        db.session.commit()  # Commit dulu agar user.id dan category.id teris
        
        report = Report(
            title='Test Report',
            description='Test Description',
            location='Test Location',
            category_id=category.id,
            user_id=user.id
        )
        
        db.session.add_all([user, category, report])
        db.session.commit()
        
        comment = Comment(
            content='Test Comment',
            report_id=report.id,
            user_id=user.id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        self.assertIsNotNone(comment.id)
        self.assertEqual(comment.author, user)
        self.assertEqual(comment.report, report)

if __name__ == '__main__':
    unittest.main()