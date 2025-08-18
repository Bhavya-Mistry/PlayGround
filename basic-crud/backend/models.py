from extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)            # bcrypt hash
    api_key = db.Column(db.String(128), unique=True, nullable=False)
    credits = db.Column(db.Integer, nullable=False, default=0)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(),
                           onupdate=db.func.now(), nullable=False)

    # Optional helpers (not required if you hash in routes)
    def set_password(self, plain_password: str):
        self.password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    def check_password(self, plain_password: str) -> bool:
        return bcrypt.check_password_hash(self.password, plain_password)
