import random
import threading

import requests

from tests.end_tests.utils import ClientSession


def modify_doc(i):
    session = ClientSession(domain="http://localhost:5000")
    session.setup_user(f"user_{i}")

    session.create_document()

    for _ in range(300):
        try:
            docs = session.get_documents().json()["documents"]
            doc = random.choice(docs)
            session.modify_document(
                doc,
                data=str(random.randbytes(8)),
                params={"rc_sleep": random.random() / 100},
                expected_status=[200, 409],
            )
        except requests.ConnectionError:
            print("Oooops")

    print("OK")


def main():
    threads = []
    for i in range(3):
        thread = threading.Thread(target=modify_doc, args=(i,))
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
