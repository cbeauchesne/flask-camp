if __name__ == "__main__":
    from api.core import create_app

    app = create_app(sql_echo=True)
    app.create_all()
