from flask import request

def parse_pagination_params(default_page=1, default_size=12, max_size=50):
    """
    Parse pagination parameters from request args.
    Raises ValueError if parameters are not valid integers.
    This allows route handlers to return proper 400 Bad Request responses.
    """
    page_str = request.args.get('page')
    page_size_str = request.args.get('page_size')
    
    # Parse page parameter
    if page_str is not None:
        try:
            page = int(page_str)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid page parameter: {page_str}")
    else:
        page = default_page
    
    # Parse page_size parameter
    if page_size_str is not None:
        try:
            page_size = int(page_size_str)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid page_size parameter: {page_size_str}")
    else:
        page_size = default_size

    # Validate and clamp values
    page = max(1, page)
    page_size = min(max(1, page_size), max_size)

    return page, page_size
