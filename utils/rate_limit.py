from flask import request, jsonify
from functools import wraps
from collections import defaultdict
from time import time


_request_counts = defaultdict(lambda: defaultdict(list))
_CLEANUP_INTERVAL = 3600


def _cleanup_old_entries():
    current_time = time()
    for endpoint in list(_request_counts.keys()):
        for identifier in list(_request_counts[endpoint].keys()):
            if not _request_counts[endpoint][identifier]:
                del _request_counts[endpoint][identifier]
        if not _request_counts[endpoint]:
            del _request_counts[endpoint]


def rate_limit(max_requests=5, window_seconds=900):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            identifier = request.remote_addr
            
            if request.is_json and isinstance(request.json, dict):
                phone = request.json.get('phone')
                email = request.json.get('email')
                if phone:
                    identifier = f"phone:{phone}"
                elif email:
                    identifier = f"email:{email}"
            
            endpoint = request.endpoint
            current_time = time()
            
            request_times = _request_counts[endpoint][identifier]
            request_times[:] = [t for t in request_times if current_time - t < window_seconds]
            
            if not request_times and identifier in _request_counts[endpoint]:
                del _request_counts[endpoint][identifier]
            
            if len(request_times) >= max_requests:
                return jsonify({
                    'error': 'Too many requests. Please try again later.'
                }), 429
            
            request_times.append(current_time)
            
            if int(current_time) % _CLEANUP_INTERVAL == 0:
                _cleanup_old_entries()
            
            return f(*args, **kwargs)
        
        return wrapped
    return decorator
