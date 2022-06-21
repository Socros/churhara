from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username

def deploy():
	"""Run deployment tasks."""
	from app import create_app,db
	from flask_migrate import upgrade,migrate,init,stamp
	from models import User

	app = create_app()
	app.app_context().push()
	db.create_all()

	# migrate database to latest revision
	init()
	stamp()
	migrate()
	upgrade()
	
deploy()