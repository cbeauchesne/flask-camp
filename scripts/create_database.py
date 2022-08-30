if __name__ == "__main__":
    from api.core import create_app

    app = create_app()
    app.create_all()
