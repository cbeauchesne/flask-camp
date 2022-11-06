from flask_camp.views.content import document, documents, merge, user_tags, version, versions
from flask_camp.views.account import current_user, email_validation, reset_password, user, user_login, users
from flask_camp.views import healthcheck, home, logs


def test_content():
    assert hasattr(document, "get")
    assert hasattr(document, "post")
    assert hasattr(document, "put")
    assert hasattr(document, "delete")

    assert hasattr(documents, "get")
    assert hasattr(documents, "post")
    # assert hasattr(documents, "put")
    # assert hasattr(documents, "delete")

    # assert hasattr(merge, "get")
    # assert hasattr(merge, "post")
    assert hasattr(merge, "put")
    # assert hasattr(merge, "delete")

    assert hasattr(user_tags, "get")
    assert hasattr(user_tags, "post")
    # assert hasattr(user_tags, "put")
    assert hasattr(user_tags, "delete")

    assert hasattr(version, "get")
    # assert hasattr(version, "post")
    assert hasattr(version, "put")
    assert hasattr(version, "delete")

    assert hasattr(versions, "get")
    # assert hasattr(versions, "post")
    # assert hasattr(versions, "put")
    # assert hasattr(versions, "delete")


def test_account():
    assert hasattr(current_user, "get")
    # assert hasattr(current_user, "post")
    # assert hasattr(current_user, "put")
    # assert hasattr(current_user, "delete")

    assert hasattr(email_validation, "get")
    # assert hasattr(email_validation, "post")
    assert hasattr(email_validation, "put")
    # assert hasattr(email_validation, "delete")

    # assert hasattr(reset_password, "get")
    # assert hasattr(reset_password, "post")
    assert hasattr(reset_password, "put")
    # assert hasattr(reset_password, "delete")

    assert hasattr(user, "get")
    # assert hasattr(user, "post")
    assert hasattr(user, "put")
    # assert hasattr(user, "delete")

    # assert hasattr(user_login, "get")
    # assert hasattr(user_login, "post")
    assert hasattr(user_login, "put")
    assert hasattr(user_login, "delete")

    assert hasattr(users, "get")
    assert hasattr(users, "post")
    # assert hasattr(users, "put")
    # assert hasattr(users, "delete")


def test_miscs():
    assert hasattr(home, "get")
    assert hasattr(logs, "get")
    assert hasattr(healthcheck, "get")
