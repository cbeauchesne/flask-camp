from tests.end_tests.utils import ClientSession


if __name__ == "__main__":
    admin = ClientSession(domain="http://localhost:5000")
    admin.login_user("admin")

    moderator = ClientSession(domain="http://localhost:5000")
    moderator.setup_user("moderator")

    admin.modify_user(moderator.logged_user["id"], roles=["moderator"], comment="I trust him")

    user = ClientSession(domain="http://localhost:5000")
    user.setup_user("user")

    doc = user.create_document({}, comment="create").json()["document"]
    admin.delete_document(doc, comment="deletion")

    doc = user.create_document({}, comment="create").json()["document"]
    user.protect_document(doc, comment="protect", expected_status=403)
    moderator.protect_document(doc, comment="protect")

    user.modify_document(doc, data={}, comment="modify", expected_status=403)  # why ?
    moderator.modify_document(doc, data={}, comment="modify", expected_status=200)

    doc_2 = user.create_document(data={}, comment="protect").json()["document"]
    user.modify_document(doc_2, data={}, comment="protect", expected_status=200)

    anonymous = ClientSession(domain="http://localhost:5000")
    anonymous.get_documents()

    # admin.block_user(user)
