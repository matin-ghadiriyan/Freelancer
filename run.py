import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Debug is controlled by the environment so production stays safe.
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug)