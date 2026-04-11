# Tests

This directory contains all tests for the project. Read this before writing or modifying a test.

## Running tests

```bash
pytest tests/
```

Run a single file while iterating:

```bash
pytest tests/test_<name>.py
```

## File and function naming

| Thing | Pattern | Example |
|---|---|---|
| Test file | `test_<feature>.py` | `test_auth.py`, `test_otp.py` |
| Test function | `test_<feature>_<scenario>` | `test_login_invalid_password` |
| Helper function | `_<name>` | `_make_token`, `_insert_user` |

## Fixtures and mocking

Shared fixtures are in `conftest.py` — use them.

Available: `client`, `app`, `mock_db`, `runner`.

Prefer `mock_db` over other database mocking approaches. Use `@patch(...)` or `with patch(...)` for external boundaries and side effects. Don't introduce custom database simulators when existing fixtures already cover the case.

```python
# good
def test_user_creation(mock_db):
    ...

# avoid — mock_db already handles this
def test_user_creation():
    db = FakeDatabase()
    ...
```

## Writing tests

Follow **Arrange → Act → Assert**. Assert the status code and the fields that matter — not the entire response body.

```python
def test_login_success(client, mock_db):
    #---- arrange ----
    mock_db.users.insert_one({"email": "user@example.com", "password": "hashed"})

    #---- act ----
    res = client.post("/api/auth/login", json={"email": "user@example.com", "password": "secret"})

    #---- assert ----
    assert res.status_code == 200
    assert res.get_json()["token"] is not None
```

Every test must cover the failure path too, especially for auth, permissions, and validation:

```python
def test_login_wrong_password(client, mock_db):
    mock_db.users.insert_one({"email": "user@example.com", "password": "hashed"})

    res = client.post("/api/auth/login", json={"email": "user@example.com", "password": "wrong"})

    assert res.status_code == 401
    assert "token" not in res.get_json()
```

## Section dividers

Use this format to separate logical groups within a test file:

```python
#---- section name ----
```

Do not use multi-line dashed blocks.

## Before opening a PR

- Tests cover both positive and negative scenarios.
- Tests are isolated — no shared or external state between them.
- All tests pass locally.