"""
Taskboard
I'm putting this here for the sole purpose of fixing linting issues.
"""
import os
import datetime
from flask import Flask, render_template, request, redirect, url_for
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv, dotenv_values

load_dotenv()

def create_app():
    """
    Create and configure the Flask application.
    returns: app: the Flask application object
    """

    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )
    # load flask config from env variables
    config = dotenv_values()
    app.config.from_mapping(config)

    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]

    try:
        cxn.admin.command("ping")
        print(" *", "Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e)

    @app.route("/")
    def home():
        """
        Route for the home page.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        docs = db.messages.find({}).sort("created_at", -1)
        return render_template("index.html", docs=docs)

    @app.route("/edit-task")
    def edit_task():
        return render_template("edit_task.html")

    @app.route("/edit-task", methods=["POST"])
    def edit_task_post():
        return redirect(url_for("home"))

    @app.errorhandler(Exception)
    def handle_error(e):
        """
        Output any errors - good for debugging.
        Args:
            e (Exception): The exception object.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        return render_template("error.html", error=e)

    return app


app = create_app()

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    FLASK_ENV = os.getenv("FLASK_ENV")
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")

    app.run(port=FLASK_PORT)
