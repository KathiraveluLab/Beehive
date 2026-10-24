"""Admin list endpoints must bound limit/offset/page/days and answer bad values with 400."""

import datetime

import pytest
from bson import ObjectId


@pytest.fixture
def admin_headers(app):
    with app.app_context():
        from utils.jwt_auth import create_access_token

        token = create_access_token(str(ObjectId()), "admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def many_rows(mock_db):
    now = datetime.datetime.now(datetime.timezone.utc)
    mock_db.users.insert_many(
        [{"username": f"user{i}", "email": f"user{i}@example.com"} for i in range(130)]
    )
    mock_db.notifications.insert_many(
        [
            {"seen": False, "timestamp": now - datetime.timedelta(seconds=i)}
            for i in range(70)
        ]
    )


def _rows(response, key):
    return response.get_json()[key]


def test_users_default_page_size(client, admin_headers, many_rows):
    response = client.get("/api/admin/users", headers=admin_headers)

    assert response.status_code == 200
    assert len(_rows(response, "users")) == 10


def test_users_limit_zero_is_not_unlimited(client, admin_headers, many_rows):
    response = client.get("/api/admin/users?limit=0", headers=admin_headers)

    assert response.status_code == 200
    assert len(_rows(response, "users")) == 1


def test_users_limit_is_capped(client, admin_headers, many_rows):
    response = client.get("/api/admin/users?limit=100000", headers=admin_headers)

    assert response.status_code == 200
    assert len(_rows(response, "users")) == 100
    assert response.get_json()["totalCount"] == 130


def test_users_negative_offset_is_treated_as_zero(client, admin_headers, many_rows):
    response = client.get("/api/admin/users?limit=5&offset=-10", headers=admin_headers)

    assert response.status_code == 200
    assert [u["name"] for u in _rows(response, "users")] == [
        f"user{i}" for i in range(5)
    ]


@pytest.mark.parametrize("query", ["limit=abc", "offset=1.5", "limit=", "offset=x"])
def test_users_non_integer_params_get_400(client, admin_headers, many_rows, query):
    response = client.get(f"/api/admin/users?{query}", headers=admin_headers)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_notifications_limit_zero_is_not_unlimited(client, admin_headers, many_rows):
    response = client.get("/api/admin/notifications?limit=0", headers=admin_headers)

    assert response.status_code == 200
    assert len(_rows(response, "notifications")) == 1


def test_notifications_limit_is_capped(client, admin_headers, many_rows):
    response = client.get(
        "/api/admin/notifications?limit=100000", headers=admin_headers
    )

    assert len(_rows(response, "notifications")) == 50


def test_notifications_page_zero_is_page_one(client, admin_headers, many_rows):
    first = client.get("/api/admin/notifications?page=1&limit=5", headers=admin_headers)
    zero = client.get("/api/admin/notifications?page=0&limit=5", headers=admin_headers)

    assert zero.status_code == 200
    assert zero.get_json()["page"] == 1
    assert [n["_id"] for n in _rows(zero, "notifications")] == [
        n["_id"] for n in _rows(first, "notifications")
    ]


def test_notifications_non_integer_gets_400(client, admin_headers, many_rows):
    response = client.get("/api/admin/notifications?limit=abc", headers=admin_headers)

    assert response.status_code == 400


@pytest.mark.parametrize("days", ["abc", "1.5", ""])
def test_analytics_non_integer_days_gets_400(client, admin_headers, days):
    response = client.get(f"/api/admin/analytics?days={days}", headers=admin_headers)

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("days", "expected"), [("0", 1), ("-5", 1), ("7", 7), ("100000", 365)]
)
def test_analytics_days_are_clamped(client, admin_headers, days, expected):
    response = client.get(f"/api/admin/analytics?days={days}", headers=admin_headers)

    assert response.status_code == 200
    assert len(response.get_json()["uploads"]["trend"]) == expected


# --- parse_pagination_params (the dashboard's parser) is built on the same helper ----------------


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("", (1, 12)),
        ("?page=3&page_size=20", (3, 20)),
        ("?page=0&page_size=0", (1, 1)),
        ("?page=-4&page_size=1000", (1, 50)),
    ],
)
def test_parse_pagination_params_defaults_and_clamping(app, query, expected):
    from utils.pagination import parse_pagination_params

    with app.test_request_context(f"/x{query}"):
        assert (
            parse_pagination_params(default_page=1, default_size=12, max_size=50)
            == expected
        )


@pytest.mark.parametrize(
    ("query", "name"), [("?page=abc", "page"), ("?page_size=1.5", "page_size")]
)
def test_parse_pagination_params_rejects_non_integers(app, query, name):
    from utils.pagination import parse_pagination_params

    with app.test_request_context(f"/x{query}"):
        with pytest.raises(ValueError, match=f"Invalid {name} parameter"):
            parse_pagination_params()
