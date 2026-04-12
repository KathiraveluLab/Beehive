import re
from flask import Blueprint, request, jsonify
from utils.jwt_auth import require_admin_role
from datetime import datetime, timezone
from database.userdatahandler import (
    _get_paginated_images_by_user,
    get_recent_uploads,
    get_upload_stats,
    get_upload_analytics,
    get_user_analytics,
    unlock_account,
    get_lock_status,
)
from utils.pagination import parse_pagination_params
from utils.logger import Logger
from utils.sanitize import sanitize_api_query

logger = Logger.get_logger("adminroutes")

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

from database.databaseConfig import beehive

# Admin: Get user uploads
@admin_bp.route("/user_uploads/<user_id>")
@require_admin_role
def admin_user_images_show(user_id):
    try:
        page, page_size = parse_pagination_params(default_page=1, default_size=12, max_size=50)
        filters = {
            'q': request.args.get('q'),
            'sentiment': request.args.get('sentiment'),
            'date_filter': request.args.get('date_filter'),
            'from': request.args.get('from'),
            'to': request.args.get('to')
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        result = _get_paginated_images_by_user(user_id, page, page_size, filters if filters else None)
        return jsonify(result), 200
    except ValueError as e:
        logger.error(f"Invalid pagination parameters: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception:
        logger.error("Error fetching user uploads", exc_info=True)
        return jsonify({"error": "Failed to fetch user uploads"}), 500

# Admin: Dashboard
@admin_bp.route("/dashboard", methods=["GET"])
@require_admin_role
def get_dashboard_data():
    try:
        user = sanitize_api_query(request.args.get("user", ""))

        try:
            page = int(request.args.get("page", "1"))
            limit = int(request.args.get("limit", "10"))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid pagination parameters. 'page' and 'limit' must be integers."}), 400

        page = max(1, page)
        limit = min(max(1, limit), 50)

        from_date = None
        end_date = None
        from_date_str = request.args.get("from")
        if from_date_str:
            try:
                from_date = datetime.fromisoformat(from_date_str).replace(tzinfo=timezone.utc)
            except ValueError:
                return jsonify({"error": f"Invalid 'from' date format: {from_date_str}. Expected YYYY-MM-DD."}), 400
        end_date_str = request.args.get("to")
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            except ValueError:
                return jsonify({"error": f"Invalid 'to' date format: {end_date_str}. Expected YYYY-MM-DD."}), 400
        sort_method = request.args.get("sort")
        VALID_SORT_METHODS = ['date_desc', 'date_asc', 'user_desc', 'user_asc']
        if sort_method and sort_method not in VALID_SORT_METHODS:
            return jsonify({"error": f"Invalid sort method. Allowed values: {', '.join(VALID_SORT_METHODS)}"}), 400
        stats = get_upload_stats()
        recent_uploads, total_count = get_recent_uploads(page=page, limit=limit, username_filter=user, from_date=from_date, end_date=end_date, sort_method=sort_method)
        return jsonify({
            "stats": stats,
            "recentUploads": recent_uploads,
            "total": total_count
        }), 200

    except Exception:
        logger.error("Error fetching dashboard data", exc_info=True)
        return jsonify({"error": "Failed to fetch dashboard data"}), 500

# Admin: Analytics (Uploads only)
@admin_bp.route("/analytics", methods=["GET"])
@require_admin_role
def get_all_analytics():
    try:
        days_param = request.args.get("days", 7)
        try:
            days_ago = min(max(1, int(days_param)), 365)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid 'days' parameter"}), 400
        

        upload_data = get_upload_analytics(trend_days=days_ago)
        user_data = get_user_analytics()
        if not upload_data:
            return jsonify({"error": "Failed to retrieve analytics data"}), 500
        if not user_data:
            return jsonify({"error": "Failed to retrieve user analytics data"}), 500
        return jsonify({
            "uploads": upload_data,
            "users": user_data
        }), 200

    except Exception:
        logger.error("Error fetching analytics", exc_info=True)
        return jsonify({"error": "Failed to fetch analytics data"}), 500

# Admin: List users (paginated, searchable)

@admin_bp.route("/users", methods=["GET"])
@require_admin_role
def list_users():
    try:
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))
        query = sanitize_api_query(request.args.get("query", ""))

        # Build filter
        mongo_filter = {}
        if query:
            safe_pattern = re.escape(query)
            regex = {"$regex": safe_pattern, "$options": "i"}
            mongo_filter = {"$or": [{"username": regex}, {"email": regex}]}

        users_col = beehive.users
        total_count = users_col.count_documents(mongo_filter)

        cursor = users_col.find(mongo_filter).skip(offset).limit(limit)

        now = datetime.now(timezone.utc)
        users = []
        for u in cursor:
            lock = get_lock_status(u, now=now)
            users.append({
                "id": str(u.get("_id")),
                "user_id": str(u.get("_id")),
                "name": u.get("username") or u.get("email") or "Unknown User",
                "email": u.get("email") or "",
                "role": u.get("role", "user"),
                "lastActive": u.get("last_active") or u.get("last_seen") or None,
                "status": u.get("status", "active"),
                "image": u.get("avatar_url", ""),
                "isLocked": lock["is_locked"],
                "failedAttempts": lock["failed_attempts"],
            })

        return jsonify({"users": users, "totalCount": total_count}), 200
    except Exception:
        logger.error("Error listing users", exc_info=True)
        return jsonify({"error": "Failed to list users"}), 500


@admin_bp.route("/users/<user_id>/unlock", methods=["POST"])
@require_admin_role
def unlock_user(user_id):
    try:
        success = unlock_account(user_id)
        if success:
            return jsonify({"message": "Account unlocked successfully"}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception:
        logger.error("Error unlocking user account", exc_info=True)
        return jsonify({"error": "Failed to unlock account"}), 500


@admin_bp.route("/users/only-users", methods=["GET"])
@require_admin_role
def list_only_users():
    try:
        users_col = beehive.users
        cursor = users_col.find({}, {"_id": 1, "username": 1, "email": 1}).limit(100)
        users = []
        for u in cursor:
            users.append({
                "id": str(u.get("_id")),
                "name": u.get("username") or u.get("email") or "",
            })
        return jsonify({"users": users}), 200
    except Exception:
        logger.error("Error listing only-users", exc_info=True)
        return jsonify({"error": "Failed to list users"}), 500
