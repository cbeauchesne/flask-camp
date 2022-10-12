"""
flask_camp, Utils for flask_camp extension

Usage:
    flask_camp dev_env

Commands:
    dev_env     Start dev env, simply a redis on 6379 and a postgresql on 5432

"""

import os
import subprocess

from docopt import docopt


def main():
    args = docopt(__doc__)

    if args["dev_env"]:
        docker_file = os.path.join(os.path.dirname(__file__), "docker-compose.yml")
        subprocess.run(
            ["docker", "compose", "-f", docker_file, "up", "--remove-orphans", "--wait", "-d", "redis", "pg"],
            check=True,
        )
