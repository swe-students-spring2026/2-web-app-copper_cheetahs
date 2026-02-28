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
        # docs = db.messages.find({}).sort("created_at", -1)
        # return render_template("index.html", docs=docs)
        return render_template("index.html")

    @app.route("/login")
    def login():
        """
        Route for the login page.
        """
        return render_template("login.html")


    """
    <form> {
        input name='title'
        input name='description'
        input name='priority'
        input name='due_date'
        input name='status'
        input name='assigned'

        button submit
    }
    """

    @app.route("/add-task")
    def add_task():
        return render_template("add_task.html")
    
    @app.route("/add-task",  methods=["POST"])
    def add_task_post():
        print(request.form)
        tempDoc = {
            'name': request.form.get('title'),
            'description': request.form.get('description'),
            'priority': request.form.get('priority'),
            'due_date': request.form.get('due_date'),
            'namstatuse': request.form.get('status'),
            'assigned': request.form.get('assigned'),
        }
        
        taskID = db.taskList.insert_one(tempDoc)

        # test = db.taskList.find({})
        # print(test)
        return redirect(url_for("home"))
    
    """
    python backend/app.py
    """




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

