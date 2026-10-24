from flask import request

# Upper bound for a page number; far beyond any real collection, it only keeps the value sane.
_MAX_PAGE = 10**9


def parse_bounded_int(name, default, min_value, max_value):
    """
    Read an integer query parameter and clamp it to [min_value, max_value].
    Raises ValueError if the value is present but not an integer, so route handlers
    can return a 400 instead of an unhandled error.
    """
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid {name} parameter: {raw}")
    return min(max(value, min_value), max_value)


def parse_pagination_params(default_page=1, default_size=12, max_size=50):
    """
    Parse pagination parameters from request args.
    Raises ValueError if parameters are not valid integers.
    This allows route handlers to return proper 400 Bad Request responses.
    """
    page = parse_bounded_int('page', default_page, 1, _MAX_PAGE)
    page_size = parse_bounded_int('page_size', default_size, 1, max_size)
    return page, page_size
