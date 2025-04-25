# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), unique=True, nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime,
                             default=datetime.utcnow,
                             onupdate=datetime.utcnow)

class Session(db.Model):
    __tablename__ = "sessions"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    context    = db.Column(db.Text, default="")          # 存储对话历史 Prompt
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at   = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref=db.backref("sessions", lazy=True))

class Image(db.Model):
    __tablename__ = "images"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    uploaded_at= db.Column(db.DateTime, default=datetime.utcnow)

    user    = db.relationship("User", backref=db.backref("images", lazy=True))
    session = db.relationship("Session", backref=db.backref("images", lazy=True))

class Question(db.Model):
    __tablename__ = "questions"
    id            = db.Column(db.Integer, primary_key=True)
    session_id    = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    user_question = db.Column(db.Text, nullable=False)
    answer        = db.Column(db.Text, nullable=False)
    asked_at      = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship("Session", backref=db.backref("questions", lazy=True))
