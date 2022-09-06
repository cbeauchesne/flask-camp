#!/usr/bin/env python3

if __name__ == "__main__":
    from sys import stdout
    import logging
    from cms.application import Application
    from cms import database

    database.add_handler(logging.StreamHandler(stdout))
    app = Application()
    app.create_all()
