if __name__ == "__main__":
    from sys import stdout
    from cms.application import Application
    from cms import database

    database.add_logger(stdout)
    app = Application()
    app.create_all()
