import datetime
import pytest
from bson.objectid import ObjectId
from utils.jwt_auth import create_access_token

# ---- Helper Functions ----


def _create_test_user(mock_db, username="testuser", email="test@example.com"):
    """Create a test user and return their ObjectId"""
    user_id = ObjectId()
    mock_db.users.insert_one({"_id": user_id, "username": username, "email": email})
    return user_id


def _create_test_images(mock_db, user_id, images_data):
    """Create test images from a list of dictionaries"""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    processed_images = []

    for img in images_data:
        processed_img = {
            "user_id": user_id,
            "filename": img["filename"],
            "url": f"https://example.com/{img['filename']}",
            "title": img["title"],
            "description": img["description"],
            "sentiment": img.get("sentiment", "neutral"),
            "created_at": img.get("created_at", now_utc),
        }
        if "audio_filename" in img:
            processed_img["audio_filename"] = img["audio_filename"]
        processed_images.append(processed_img)

    if processed_images:
        mock_db.images.insert_many(processed_images)


# ---- Test Cases ----


def test_unauthorized_no_token(client, mock_db):
    """GET /api/admin/dashboard - No authentication"""
    response = client.get("/api/admin/dashboard")
    assert response.status_code == 401


def test_non_admin_user(client, mock_db, app):
    """GET /api/admin/dashboard - User without admin role"""
    with app.app_context():
        user_token = create_access_token(user_id="regular_user", role="user")

    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


def test_empty_dashboard(client, mock_db, admin_token):
    """GET /api/admin/dashboard - No data"""
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.get_json()

    assert data["stats"]["totalImages"] == 0  # no images exist in the database
    assert data["stats"]["totalVoiceNotes"] == 0  # no voice notes exist in the database
    assert data["stats"]["totalMedia"] == 0  # 0 images + 0 voice notes
    assert data["recentUploads"] == []
    assert data["total"] == 0


def test_dashboard_with_data(client, mock_db, admin_token):
    """GET /api/admin/dashboard - With data"""
    user_id = _create_test_user(mock_db)
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    _create_test_images(
        mock_db,
        user_id,
        [
            {
                "filename": "img1.webp",
                "title": "First Image",
                "description": "A test image from yesterday",
                "sentiment": "neutral",
                "created_at": now_utc - datetime.timedelta(days=1),  # created yesterday
            },
            {
                "filename": "img2.webp",
                "title": "Second Image",
                "description": "A test image with audio",
                "sentiment": "happy",
                "audio_filename": "audio1.webm",
                "created_at": now_utc,  # created now
            },
        ],
    )

    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.get_json()

    assert data["stats"]["totalImages"] == 2  # 2 images exist in the database
    assert (
        data["stats"]["totalVoiceNotes"] == 1
    )  # 1 voice note exists in the database from img2.webp
    assert data["stats"]["totalMedia"] == 3  # 2 images + 1 voice note
    assert len(data["recentUploads"]) == 2  # 2 recent uploads
    assert data["total"] == 2

    recent = data["recentUploads"]
    # Most recent should be first (sorted by created_at descending)
    assert recent[0]["filename"] == "img2.webp"
    assert recent[0]["user"] == "testuser"
    assert recent[0]["title"] == "Second Image"
    assert recent[0]["sentiment"] == "happy"
    assert recent[0]["audio_filename"] == "audio1.webm"
    assert recent[0]["description"] == "A test image with audio"

    assert recent[1]["filename"] == "img1.webp"
    assert recent[1]["user"] == "testuser"
    assert recent[1]["title"] == "First Image"
    assert recent[1]["sentiment"] == "neutral"
    assert recent[1].get("audio_filename", "") == ""
    assert recent[1]["description"] == "A test image from yesterday"


@pytest.mark.parametrize(
    "page,limit,expected_upload_count",
    [
        (None, None, 10),  # default (page=1, limit=10)
        (1, 5, 5),  # custom limit
        (2, 5, 5),  # page 2
        (1, 20, 15),  # limit larger than total
    ],
)
def test_pagination_variations(
    client, mock_db, admin_token, page, limit, expected_upload_count
):
    """GET /api/admin/dashboard - Pagination works correctly with various limits"""
    user_id = _create_test_user(mock_db)
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    images_data = [
        {
            "filename": f"img{i}.webp",
            "title": f"Image {i}",
            "description": f"Test image {i}",
            "sentiment": "neutral",
            "created_at": now_utc - datetime.timedelta(hours=i),
        }
        for i in range(15)
    ]
    _create_test_images(mock_db, user_id, images_data)

    query_params = []
    if page is not None:
        query_params.append(f"page={page}")
    if limit is not None:
        query_params.append(f"limit={limit}")

    kwargs = {}
    if query_params:
        kwargs["query_string"] = "&".join(query_params)

    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
        **kwargs,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["recentUploads"]) == expected_upload_count
    assert data["total"] == 15


def test_invalid_pagination_parameters(client, mock_db, admin_token):
    """GET /api/admin/dashboard - Invalid page/limit parameters"""
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
        query_string="page=invalid&limit=10",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


@pytest.mark.parametrize(
    "filter_param,date_offset,expected_filename",
    [
        ("from", 1, "recent_img.webp"),  # from recent_date -> gets only recent
        ("to", 10, "old_img.webp"),  # to old_date -> gets only old
    ],
)
def test_date_filtering(
    client, mock_db, admin_token, filter_param, date_offset, expected_filename
):
    """GET /api/admin/dashboard - Date range filtering from and to parameters"""
    user_id = _create_test_user(mock_db)
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    _create_test_images(
        mock_db,
        user_id,
        [
            {
                "filename": "old_img.webp",
                "title": "Old Image",
                "description": "Old",
                "created_at": now_utc - datetime.timedelta(days=10),
            },
            {
                "filename": "recent_img.webp",
                "title": "Recent Image",
                "description": "Recent",
                "created_at": now_utc - datetime.timedelta(days=1),
            },
        ],
    )

    filter_date = (now_utc - datetime.timedelta(days=date_offset)).date()

    if filter_param == "from":
        query_string = f"from={filter_date}"
    else:
        query_string = f"to={filter_date}"

    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
        query_string=query_string,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["recentUploads"]) == 1
    assert data["recentUploads"][0]["filename"] == expected_filename
    assert data["total"] == 1


def test_invalid_date_format(client, mock_db, admin_token):
    """GET /api/admin/dashboard - Invalid date format"""
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
        query_string="from=invalid-date",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "date format" in data["error"].lower()


@pytest.mark.parametrize(
    "username,email,query",
    [
        ("O'Brien", "ob@example.com", "O'Brien"),
        ("Müller", "mu@example.com", "Müller"),
        ("anna", "anna+work@example.com", "anna+work@example.com"),
    ],
)
def test_users_search_matches_special_characters(
    client, mock_db, admin_token, username, email, query
):
    """GET /api/admin/users?query= - names/emails with ' + or non-ASCII letters"""
    _create_test_user(mock_db, username=username, email=email)
    _create_test_user(mock_db, username="plainuser", email="plain@example.com")

    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        query_string={"query": query},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert [u["name"] for u in data["users"]] == [username]


@pytest.mark.parametrize("value", ["O'Brien", "Müller", "anna+work@example.com"])
def test_sanitize_api_query_keeps_real_usernames_and_emails(value):
    """The dashboard 'user' filter relies on this keeping stored names intact"""
    from utils.sanitize import sanitize_api_query

    assert sanitize_api_query(value) == value
