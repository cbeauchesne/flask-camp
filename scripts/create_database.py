#!/usr/bin/env python3

if __name__ == "__main__":
    import logging
    import sys
    from flask_camp import config
    from flask_camp.application import Application

    app = Application(config.Development)

    logging.getLogger("sqlalchemy").addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger("sqlalchemy").setLevel(logging.INFO)

    with app.app_context():
        app.init_databases()
