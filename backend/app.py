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

        return redirect(url_for("dev_tasks"))
    
    @app.route("/dev/tasks")
    def dev_tasks():
        """
        Route for the dev tasks
        """
        # docs = db.messages.find({}).sort("created_at", -1)
        # return render_template("index.html", docs=docs)

        #temporary routing task page as home for testing
        
        filters = {}

        search_input = request.args.get("search")

        status = request.args.get("status") or "Todo"
        priority = request.args.get("priority")
        assigned = request.args.get("assigned")

        due_before = request.args.get("due_before")
        due_after = request.args.get("due_after")

        if search_input:
            filters["$or"] = [{"name": {"$regex": search_input, "$options": "i"}}, {"description": {"$regex": search_input, "$options": "i"}}]

        if status:
            filters["status"] = status

        if priority:
            filters["priority"] = priority

        if assigned:
            if assigned == "None":
                filters["assigned"] = None
            else:
                filters["assigned"] = assigned

        if due_before or due_after:
            filters["due_date"] = {}
            
            if due_before:
                filters["due_date"]["$lte"] = datetime.datetime.strptime(due_before, "%Y-%m-%d")

            if due_after:
                filters["due_date"]["$gte"] = datetime.datetime.strptime(due_after, "%Y-%m-%d")

        sort_by = request.args.get("sort_by") or "due_date"
        order =int(request.args.get("order") or 1)

        # This handles the sorting for priotity as it would else do it alphabetically instead
        if sort_by == "priority":
            tasks = list(db.devTasks.find(filters))
            priority_map = {"High": 1, "Medium": 2, "Low": 3}
            tasks.sort(key=lambda x: priority_map.get(x.get('priority'), 100), reverse=(order == -1))
        else:
            tasks = list(db.devTasks.find(filters).collation({"locale": "en", "strength": 2}).sort(sort_by, order))

        # Avoids crashes if assigned developer is "NONE"
        all_assigned_full = db.devTasks.distinct("assigned")
        all_assigned = [user for user in db.devTasks.distinct("assigned") if user is not None]
        has_unassigned = None in all_assigned_full

        return render_template(
            "taskList.html",
            taskList = tasks,
            has_unassigned=has_unassigned,
            assigned_users=sorted(all_assigned, key=lambda x: x.lower()),
            current_filters = request.args,
            current_status = status
        )
    

    @app.route("/login")
    def login():
        # Route for the login page.
        return render_template("login.html")


    # add-task
    @app.route("/add-task")
    def add_task():
        return render_template("add_task.html")
    
    @app.route("/add-task",  methods=["POST"])
    def add_task_post():
        tempDoc = {
            'name': request.form.get('title'),
            'description': request.form.get('description'),
            'priority': request.form.get('priority'),
            'due_date': datetime.datetime.strptime(request.form.get('due_date'), "%Y-%m-%d"),
            'status': request.form.get('status'),
            'assigned': request.form.getlist('assigned'),
        }

        taskID = db.devTasks.insert_one(tempDoc)
        return redirect(url_for("home"))
    

    # edit-task
    @app.route("/edit-task/<task_id>")
    def edit_task(task_id):
        task = db.devTasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            return "Task not found", 404
        return render_template("edit_task.html", task=task)
    
    @app.route("/edit-task/<task_id>/edit", methods=["POST"])
    def edit_task_post(task_id):
        updated_fields = {
            "name": request.form.get("title"),
            "description": request.form.get("description"),
            "priority": request.form.get("priority"),
            "due_date": datetime.datetime.strptime(request.form.get("due_date"), "%Y-%m-%d"),
            "status": request.form.get("status"),
            "assigned": request.form.getlist("assigned"),
        }

        db.devTasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": updated_fields}
        )

        return redirect(url_for("home"))

    # delete-task
    @app.route("/tasks/<task_id>/delete", methods=["GET"])
    def delete_task_confirm(task_id):
        task = db.devTasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            return "Task not found", 404
        return render_template("delete_task_confirm.html", task=task)
    
    @app.route("/tasks/<task_id>/delete", methods=["POST"])
    def delete_task(task_id):
        db.devTasks.delete_one({"_id": ObjectId(task_id)})
        return redirect(url_for("home"))


    # error
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

