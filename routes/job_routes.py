from flask import Blueprint, request, jsonify
from extensions import db, limiter
from models.job import Job
from routes.auth_utils import token_required, api_key_required
from datetime import datetime
from sqlalchemy import or_

job_bp = Blueprint("job", __name__)

VALID_STATUSES = ["Applied", "Interview", "Selected", "Rejected", "Pending"]
VALID_JOB_TYPES = ["Full-time", "Part-time", "Internship", "Remote", "Contract"]


@job_bp.route("/jobs", methods=["POST"])
@token_required
def add_job(current_user):
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    company_name = data.get("company_name")
    job_role = data.get("job_role")
    status = data.get("status", "Applied")
    applied_date = data.get("applied_date")
    location = data.get("location")
    job_type = data.get("job_type")
    notes = data.get("notes")

    if not company_name or not job_role or not applied_date:
        return jsonify({
            "success": False,
            "message": "Company name, job role and applied date are required"
        }), 400

    company_name = company_name.strip()
    job_role = job_role.strip()
    location = location.strip() if location else None
    job_type = job_type.strip() if job_type else None
    notes = notes.strip() if notes else None

    if len(company_name) < 2:
        return jsonify({
            "success": False,
            "message": "Company name must be at least 2 characters"
        }), 400

    if len(job_role) < 2:
        return jsonify({
            "success": False,
            "message": "Job role must be at least 2 characters"
        }), 400

    if status not in VALID_STATUSES:
        return jsonify({
            "success": False,
            "message": "Invalid status value"
        }), 422

    if job_type and job_type not in VALID_JOB_TYPES:
        return jsonify({
            "success": False,
            "message": "Invalid job type value"
        }), 422

    try:
        applied_date_obj = datetime.strptime(applied_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Applied date must be in YYYY-MM-DD format"
        }), 400

    new_job = Job(
        company_name=company_name,
        job_role=job_role,
        status=status,
        applied_date=applied_date_obj,
        location=location,
        job_type=job_type,
        notes=notes,
        user_id=current_user.id
    )

    db.session.add(new_job)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Job added successfully",
        "job_id": new_job.id
    }), 201


@job_bp.route("/jobs", methods=["GET"])
@token_required
def get_jobs(current_user):
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int)

    if page < 1 or limit < 1:
        return jsonify({
            "success": False,
            "message": "Page and limit must be positive numbers"
        }), 400

    query = Job.query.filter_by(user_id=current_user.id).order_by(Job.id.desc())

    paginated_jobs = query.paginate(
        page=page,
        per_page=limit,
        error_out=False
    )

    job_list = []

    for job in paginated_jobs.items:
        job_list.append({
            "id": job.id,
            "company_name": job.company_name,
            "job_role": job.job_role,
            "status": job.status,
            "applied_date": job.applied_date.strftime("%Y-%m-%d"),
            "location": job.location,
            "job_type": job.job_type,
            "notes": job.notes,
            "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({
        "success": True,
        "message": "Jobs fetched successfully",
        "pagination": {
            "current_page": paginated_jobs.page,
            "limit": paginated_jobs.per_page,
            "total_jobs": paginated_jobs.total,
            "total_pages": paginated_jobs.pages,
            "has_next": paginated_jobs.has_next,
            "has_prev": paginated_jobs.has_prev
        },
        "jobs": job_list
    }), 200


@job_bp.route("/jobs/<int:job_id>", methods=["GET"])
@token_required
def get_single_job(current_user, job_id):
    job = Job.query.filter_by(
        id=job_id,
        user_id=current_user.id
    ).first()

    if not job:
        return jsonify({
            "success": False,
            "message": "Job not found"
        }), 404

    job_data = {
        "id": job.id,
        "company_name": job.company_name,
        "job_role": job.job_role,
        "status": job.status,
        "applied_date": job.applied_date.strftime("%Y-%m-%d"),
        "location": job.location,
        "job_type": job.job_type,
        "notes": job.notes,
        "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }

    return jsonify({
        "success": True,
        "message": "Job fetched successfully",
        "job": job_data
    }), 200


@job_bp.route("/jobs/<int:job_id>", methods=["PUT"])
@token_required
def update_job(current_user, job_id):
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    job = Job.query.filter_by(
        id=job_id,
        user_id=current_user.id
    ).first()

    if not job:
        return jsonify({
            "success": False,
            "message": "Job not found"
        }), 404

    if "company_name" in data and not data.get("company_name").strip():
        return jsonify({
            "success": False,
            "message": "Company name cannot be empty"
        }), 400

    if "job_role" in data and not data.get("job_role").strip():
        return jsonify({
            "success": False,
            "message": "Job role cannot be empty"
        }), 400

    if "status" in data and data.get("status") not in VALID_STATUSES:
        return jsonify({
            "success": False,
            "message": "Invalid status value"
        }), 422

    if "job_type" in data and data.get("job_type") and data.get("job_type") not in VALID_JOB_TYPES:
        return jsonify({
            "success": False,
            "message": "Invalid job type value"
        }), 422

    if "company_name" in data:
        job.company_name = data.get("company_name").strip()

    if "job_role" in data:
        job.job_role = data.get("job_role").strip()

    if "status" in data:
        job.status = data.get("status")

    if "applied_date" in data:
        try:
            job.applied_date = datetime.strptime(
                data.get("applied_date"),
                "%Y-%m-%d"
            ).date()
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Applied date must be in YYYY-MM-DD format"
            }), 400

    if "location" in data:
        job.location = data.get("location").strip() if data.get("location") else None

    if "job_type" in data:
        job.job_type = data.get("job_type").strip() if data.get("job_type") else None

    if "notes" in data:
        job.notes = data.get("notes").strip() if data.get("notes") else None

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Job updated successfully"
    }), 200


@job_bp.route("/jobs/<int:job_id>", methods=["DELETE"])
@token_required
def delete_job(current_user, job_id):
    job = Job.query.filter_by(
        id=job_id,
        user_id=current_user.id
    ).first()

    if not job:
        return jsonify({
            "success": False,
            "message": "Job not found"
        }), 404

    db.session.delete(job)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Job deleted successfully"
    }), 200


@job_bp.route("/jobs/search", methods=["GET"])
@token_required
def search_jobs(current_user):
    search = request.args.get("search")
    status = request.args.get("status")
    job_type = request.args.get("job_type")
    location = request.args.get("location")

    query = Job.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(
            or_(
                Job.company_name.ilike(f"%{search}%"),
                Job.job_role.ilike(f"%{search}%")
            )
        )

    if status:
        query = query.filter(Job.status.ilike(f"%{status}%"))

    if job_type:
        query = query.filter(Job.job_type.ilike(f"%{job_type}%"))

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    jobs = query.order_by(Job.id.desc()).all()

    job_list = []

    for job in jobs:
        job_list.append({
            "id": job.id,
            "company_name": job.company_name,
            "job_role": job.job_role,
            "status": job.status,
            "applied_date": job.applied_date.strftime("%Y-%m-%d"),
            "location": job.location,
            "job_type": job.job_type,
            "notes": job.notes,
            "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({
        "success": True,
        "message": "Jobs searched successfully",
        "total_jobs": len(job_list),
        "jobs": job_list
    }), 200


@job_bp.route("/jobs/summary", methods=["GET"])
@limiter.limit("5 per minute")
@api_key_required
@token_required
def jobs_summary(current_user):
    total_jobs = Job.query.filter_by(user_id=current_user.id).count()

    applied = Job.query.filter_by(
        user_id=current_user.id,
        status="Applied"
    ).count()

    interview = Job.query.filter_by(
        user_id=current_user.id,
        status="Interview"
    ).count()

    selected = Job.query.filter_by(
        user_id=current_user.id,
        status="Selected"
    ).count()

    rejected = Job.query.filter_by(
        user_id=current_user.id,
        status="Rejected"
    ).count()

    pending = Job.query.filter_by(
        user_id=current_user.id,
        status="Pending"
    ).count()

    return jsonify({
        "success": True,
        "message": "Job statistics fetched successfully",
        "stats": {
            "total_jobs": total_jobs,
            "applied": applied,
            "interview": interview,
            "selected": selected,
            "rejected": rejected,
            "pending": pending
        }
    }), 200