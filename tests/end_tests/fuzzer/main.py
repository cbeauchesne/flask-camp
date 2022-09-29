import random
import threading

import requests

from tests.end_tests.utils import ClientSession


class FuzzerSession(ClientSession):
    known_documents = None

    def fuzz_update_known_documents(self):
        self.known_documents = self.get_documents().json()["documents"]

    def fuzz_modify_document(self):
        if not self.known_documents:
            self.fuzz_update_known_documents()

        doc = random.choice(self.known_documents)

        rc_sleep = random.random() ** 4

        self.modify_document(
            doc,
            data=str(random.randbytes(8)),
            params={"rc_sleep": rc_sleep},
            expected_status=[200, 409],
        )

    def fuzz_get_document(self):
        if not self.known_documents:
            self.fuzz_update_known_documents()

        doc = random.choice(self.known_documents)

        self.get_document(doc)

    def fuzz_get_version(self):
        if not self.known_documents:
            self.fuzz_update_known_documents()

        doc = random.choice(self.known_documents)

        versions = self.get_versions(doc).json()["versions"]

        version = random.choice(versions)

        self.get_version(version)

    def possible_actions(self):
        return [
            self.fuzz_update_known_documents,
            self.fuzz_modify_document,
            self.fuzz_get_document,
            self.fuzz_get_version,
        ]

    def do_some_stuff(self):
        action = random.choice(self.possible_actions())

        action()


def run(i):
    session = FuzzerSession(domain="http://localhost:5000")
    session.setup_user(f"user_{i}")

    session.create_document()

    for _ in range(300):
        try:
            session.do_some_stuff()
        except requests.ConnectionError:
            print("Oooops")

    print("OK")


def main():
    threads = []
    for i in range(10):
        thread = threading.Thread(target=run, args=(i,))
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
