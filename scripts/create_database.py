#!/usr/bin/env python3

if __name__ == "__main__":
    import logging
    import sys
    from cms import config
    from cms.application import Application

    app = Application(config.Testing)

    logging.getLogger("sqlalchemy").addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger("sqlalchemy").setLevel(logging.INFO)

    app.create_all()
