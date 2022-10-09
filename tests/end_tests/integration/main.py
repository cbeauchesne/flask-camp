from tests.end_tests.utils import ClientSession


if __name__ == "__main__":
    admin = ClientSession(domain="http://localhost:5000")
    admin.login_user("admin")

    moderator = ClientSession(domain="http://localhost:5000")
    moderator.setup_user("moderator")

    admin.add_user_role(moderator.logged_user["id"], role="moderator", comment="I trust him")

    user = ClientSession(domain="http://localhost:5000")
    user.setup_user("user")

    doc = user.create_document().json()["document"]
    admin.delete_document(doc)

    doc = user.create_document().json()["document"]
    user.protect_document(doc, expected_status=403)
    moderator.protect_document(doc)

    user.modify_document(doc, expected_status=403)
    moderator.modify_document(doc, expected_status=200)

    doc_2 = user.create_document().json()["document"]
    user.modify_document(doc_2, expected_status=200)

    anonymous = ClientSession(domain="http://localhost:5000")
    anonymous.get_documents()

    # admin.block_user(user)
