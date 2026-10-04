from app import app

# Standard WSGI entry point aliases
handler = app
application = app

if __name__ == "__main__":
    app.run()
