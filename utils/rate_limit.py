from flask import request, jsonify
from functools import wraps
from collections import defaultdict
from time import time


_request_counts = defaultdict(lambda: defaultdict(list))


def rate_limit(max_requests=5, window_seconds=900):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            identifier = request.remote_addr
            
            if request.is_json and request.json:
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
            
            if len(request_times) >= max_requests:
                return jsonify({
                    'error': 'Too many requests. Please try again later.'
                }), 429
            
            request_times.append(current_time)
            return f(*args, **kwargs)
        
        return wrapped
    return decorator
