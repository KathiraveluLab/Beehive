from flask import jsonify, request


def parse_pagination_params(default_page=1, default_limit=20, max_limit=100):
    """
    Parse and validate pagination parameters from request query string.
    
    Args:
        default_page: Default page number if not provided or invalid (default: 1)
        default_limit: Default limit if not provided or invalid (default: 20)
        max_limit: Maximum allowed limit (default: 100)
    
    Returns:
        tuple: (page, limit, offset) if successful
        tuple: (error_response, status_code) if validation fails
    
    Example:
        result = parse_pagination_params()
        if isinstance(result, tuple) and len(result) == 2:
            return result[0], result[1]  # error response
        page, limit, offset = result
    """
    try:
        page = int(request.args.get("page", default_page))
        limit = int(request.args.get("limit", default_limit))
    except ValueError:
        return (
            jsonify({"error": "Invalid 'page' or 'limit' parameter. Must be an integer."}),
            400,
        )

    # Validate pagination parameters
    if page < 1:
        page = default_page
    if limit < 1:
        limit = default_limit
    if limit > max_limit:
        limit = max_limit  # Cap at max_limit items per page

    # Calculate offset
    offset = (page - 1) * limit

    return (page, limit, offset)