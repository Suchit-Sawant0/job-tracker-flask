from datetime import datetime
from extensions import db


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    job_role = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Applied")
    applied_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(150), nullable=True)
    job_type = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="jobs")