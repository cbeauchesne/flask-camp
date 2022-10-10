import collections
from datetime import datetime, timedelta
import json
import random
import string
import threading
import time

import docker

from tests.end_tests.utils import ClientSession


class FuzzerSession(ClientSession):
    def __init__(self, session_count):
        super().__init__()
        self.known_documents = None
        self.kill = False
        self.session_count = session_count

    def fuzz_get_user(self):
        self.get_users(expected_status=[200, 403])

    def fuzz_block_user(self):
        user_id = random.randint(4, self.session_count)
        while user_id == self.logged_user["id"]:
            user_id = random.randint(1, self.session_count)

        self.block_user(user_id, comment="Ha!", expected_status=(200, 400))

    def fuzz_unblock_user(self):
        users = self.get_users().json()["users"]

        for user in users:
            if user["blocked"]:
                self.block_user(user, comment="Ha!", expected_status=(200, 400))

    def fuzz_update_known_documents(self):
        self.known_documents = self.get_documents().json()["documents"]

    def fuzz_create_document(self):
        self.create_document(data=str(random.randbytes(8)), expected_status=[200, 403])

    def fuzz_modify_document(self):
        if not self.known_documents:
            self.fuzz_update_known_documents()

        doc = random.choice(self.known_documents)

        self.modify_document(
            doc,
            data=str(random.randbytes(8)),
            comment="Hop!",
            expected_status=[200, 400, 403, 409],
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

    def fuzz_login(self):
        i = random.randint(0, self.session_count - 1)
        self.login_user(f"user_{i}")

    def fuzz_merge_documents(self):
        document_to_merge = random.choice(self.known_documents)
        document_destination = random.choice(self.known_documents)

        self.merge_documents(
            document_to_merge, document_destination, comment="merge it!", expected_status=[200, 400, 403]
        )

    def fuzz_add_tag(self):
        doc = random.choice(self.known_documents)

        chars = string.ascii_letters + "-_" + string.digits
        name = "".join(random.choices(chars, k=random.randint(1, 16)))

        self.add_user_tag(name, doc)

    def fuzz_remove_tag(self):
        tags = self.get_user_tags(user=self.logged_user).json()["user_tags"]

        if len(tags) != 0:
            tag = random.choice(tags)
            self.remove_user_tag(tag["name"], tag["document_id"])

    def possible_actions(self):
        result = [
            (self.fuzz_update_known_documents, 30),
            (self.fuzz_get_document, 50),
            (self.fuzz_get_version, 5),
            (self.get_logs, 1),
        ]

        if self.is_anonymous:
            result += [(self.fuzz_login, 1)]
        else:
            result += [
                (self.get_current_user, 1),
                (self.logout_user, 1),
                (self.fuzz_create_document, 5),
                (self.fuzz_modify_document, 20),
                (self.fuzz_add_tag, 5),
                (self.fuzz_remove_tag, 5),
            ]

        if self.is_moderator:
            result += [
                (self.fuzz_block_user, 1),
                (self.fuzz_unblock_user, 1),
                (self.fuzz_get_user, 1),
                (self.fuzz_merge_documents, 3),
            ]

        return [item[0] for item in result], [item[1] for item in result]

    def do_some_stuff(self):
        possible_actions, weights = self.possible_actions()
        action = random.choices(possible_actions, weights=weights, k=1)[0]

        action()

    def run(self):
        while not self.kill:
            try:
                self.do_some_stuff()
            except:  # pylint: disable=bare-except
                pass


def print_stats(sessions):
    stats = collections.defaultdict(list)
    for session in sessions:
        for key, values in session.stats.items():
            stats[key] += values

    sorted_keys = {}
    for (method, endpoint, outcome), values in stats.items():
        sort_key = f"{endpoint} {method} {outcome}"
        sorted_keys[sort_key] = (method, endpoint, outcome)

        values.sort()

    for sort_key in sorted(sorted_keys):
        (method, endpoint, outcome) = sorted_keys[sort_key]
        values = stats[(method, endpoint, outcome)]

        size = len(values)
        p_90 = int(values[int(size * 0.9)])
        p_95 = int(values[int(size * 0.95)])
        p_99 = int(values[int(size * 0.99)])
        print(f"{method:6} {endpoint:15} {len(values):5} {p_90:5}ms {p_95:5}ms {p_99:5}ms {outcome}")

    print()


def main():

    session_count = 10

    docker_client = docker.from_env()
    containers_stats = list(container.stats(decode=True) for container in docker_client.containers.list(all=True))
    docker_stats = []

    sessions = [FuzzerSession(session_count) for _ in range(session_count)]

    for i, session in enumerate(sessions):
        session.setup_user(f"user_{i}")
        session.create_document(data="init", comment="init")

    sessions[0].login_user("admin")
    sessions[0].add_user_role(2, role="moderator", comment="I trust him")
    sessions[0].add_user_role(3, role="moderator", comment="I trust him")

    threads = [threading.Thread(target=session.run) for session in sessions]

    for thread in threads:
        thread.start()

    for _ in range(50):
        next_wake_up = datetime.now() + timedelta(seconds=1)
        print_stats(sessions)
        docker_stats.append({"docker_stats": list(next(stats) for stats in containers_stats)})
        sleep_time = max(0, (next_wake_up - datetime.now()).total_seconds())
        time.sleep(sleep_time)

    for session in sessions:
        session.kill = True

    for thread in threads:
        thread.join()

    print("#" * 80)
    print_stats(sessions)
    with open("logs/docker_stats.json", mode="w", encoding="utf-8") as f:
        json.dump(docker_stats, f, indent=2)


if __name__ == "__main__":
    main()
