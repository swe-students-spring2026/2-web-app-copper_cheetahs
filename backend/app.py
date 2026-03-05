"""
Taskboard
I'm putting this here for the sole purpose of fixing linting issues.
"""
import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv, dotenv_values
import uuid

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

    app.secret_key = "tempkeyforsession"

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

        return redirect(url_for("role_screen"))
    
    @app.route("/role")
    def role_screen():
        # choose dev or stakeholder
        return render_template("role.html")
    

    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            #creates simple user and password. not encrypted or anything.
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')

            if db.users.find_one({"username": username}):
                return "User already exists", 400
            
            db.users.insert_one({
                "username": username,
                "password": password,
                "role": role
            })

            return redirect(url_for("role_screen"))
    
        return render_template("register.html")
                        

    @app.route("/dev/login", methods = ['POST', 'GET'])
    def dev_login():
        # dev login page, no actual login function 
        # just click button to go next for now
        if(request.method == 'POST'):
            username = request.form.get('username')
            password = request.form.get('password')

            # now checks if user is a developer.
            
            user = db.users.find_one({
                "username": username, 
                "password": password,
                "role": "dev"
            })
            if user:
                session['username'] = username
                session['role'] = "dev"
                return redirect(url_for("dev_projects"))
            else:
                return "Invalid credentials", 401

        return render_template("login.html")
    
    @app.route("/stk/login", methods = ['POST', 'GET'])
    def stk_login():
        # stakeholder login page, no actual login function 
        # just click button to go next for now
        if(request.method == 'POST'):
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')

            user = db.users.find_one({
                "username": username, 
                "password": password,
                "role": "stk"
            })

            if user:
                session['username'] = username
                session['role'] = "stk"
                return redirect(url_for("stk_projects"))
            else:
                return "Invalid Dev credentials", 401

        return render_template("login.html")
    
    @app.route("/stk/projects", methods = ['GET'])
    def stk_projects():
        project_list = list(db.projects.find({}))

        return render_template(
            "stakeholder_home.html",
            project_list = project_list
        )
    
    @app.route("/stk/projects/create", methods = ['GET', 'POST'])
    def stk_add_project():
        # add to project list
        if(request.method=='POST'):
            assigned = request.form.get('assigned')
            if assigned:
                assigned = assigned.strip()
            else:
                assigned = None

            tempDoc = {
                'projectID': str(uuid.uuid4()),
                'name': request.form.get('title'),
                'description': request.form.get('description'),
                'assigned': assigned
            }

            db.projects.insert_one(tempDoc)
            return redirect(url_for('stk_projects'))
        
        return render_template("add_project.html")
    
    ## START OF CHANGING STUFF TO STK

    #join project logic

    @app.route("/dev/join", methods=['GET', 'POST'])
    def join_project():
        if request.method == 'POST':
            project_id = request.form.get('project_id')
            username = session.get('username')

            if not username:
                return redirect(url_for("dev_login"))
             
            project = db.projects.find_one({"projectID": project_id})


            if not project:
                return "ProjectID not found", 404
            
            if username in project.get('assigned_devs', []):
                return "Already assigned to the project", 400
            
            db.projects.update_one(
                {"projectID": project_id},
                {"$push": {"assigned_devs": username}}
            )

            return redirect(url_for("dev_projects"))
        
        return render_template("join_project.html", prefilled_id=request.args.get('id', ''))
            
    # share project logic

    @app.route("/stk/projects/<project_id>/share", methods=["GET"])
    def share_project(project_id):
        project = db.projects.find_one({"projectID": project_id})
        if not project:
            return "Project not found", 404
        
        # external gives the full link
        invite_link = url_for('join_project', id=project_id, _external=True)

        return render_template("share_project.html", project=project, invite_link=invite_link)

    # edit-project
    @app.route("/stk/projects/edit/<project_id>")
    def edit_project(project_id):
        project = db.projects.find_one({"projectID": project_id})
        if not project:
            return "Project not found", 404
        print('hello')
        return render_template("edit_project.html", project=project, project_id=project_id)
    
    @app.route("/stk/projects/edit/<project_id>", methods=["POST"])
    def edit_project_post(project_id):
        assigned = request.form.get('assigned')
        if assigned:
            assigned = assigned.strip()
        else:
            assigned = None
        updated_fields = {
            "name": request.form.get("title"),
            "description": request.form.get("description"),
            "assigned": assigned,
        }

        db.projects.update_one(
            {"projectID": project_id},
            {"$set": updated_fields}
        )

        return redirect(url_for("stk_projects"))

    # delete-task
    @app.route("/stk/projects/<project_id>/delete", methods=["GET"])
    def delete_project_confirm(project_id):
        project = db.projects.find_one({"projectID": project_id})
        if not project:
            return "Project not found", 404
        return render_template("delete_project_confirm.html", project=project, project_id=project_id)
    
    @app.route("/stk/projects/<project_id>/delete", methods=["POST"])
    def delete_project(project_id):
        db.projects.delete_one({"projectID": project_id})
        return redirect(url_for("stk_projects"))
    
    ## END

    @app.route("/dev/projects", methods = ['GET'])
    def dev_projects():
        # dev project list

        username = session.get('username')

        if not username:
            return redirect(url_for("dev_login"))
        
        #simple check to see if the user is assgined to the project.

        project_list = list(db.projects.find({"assigned_devs": username}))

        return render_template(
            "project_home.html",
            project_list = project_list
        )

    @app.route("/dev/projects/create", methods = ['GET', 'POST'])
    def add_project():
        # add to dev project list
        if(request.method=='POST'):
            assigned = request.form.get('assigned')
            if assigned:
                assigned = assigned.strip()
            else:
                assigned = None

            tempDoc = {
                'projectID': str(uuid.uuid4()),
                'name': request.form.get('title'),
                'description': request.form.get('description'),
                'assigned': assigned
            }

            db.projects.insert_one(tempDoc)
            return redirect(url_for('dev_projects'))
        
        return render_template("add_project.html")

    @app.route("/dev/projects/<project_id>/tasks")
    def dev_tasks(project_id):
        """
        Route for the dev tasks
        """
        # docs = db.messages.find({}).sort("created_at", -1)
        # return render_template("index.html", docs=docs)

        #temporary routing task page as home for testing
        
        filters = {
            'projectID': project_id
        }

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
            "task_list.html",
            project_id = project_id,
            task_list = tasks,
            has_unassigned=has_unassigned,
            assigned_users=sorted(all_assigned, key=lambda x: x.lower()),
            current_filters = request.args,
            current_status = status
        )


    # add-task
    @app.route("/dev/<project_id>/add-task")
    def add_task(project_id):
        return render_template("add_task.html", project_id=project_id)
    
    @app.route("/dev/<project_id>/add-task",  methods=["POST"])
    def add_task_post(project_id):
        tempDoc = {
            'projectID': project_id,
            'name': request.form.get('title'),
            'description': request.form.get('description'),
            'priority': request.form.get('priority'),
            'due_date': datetime.datetime.strptime(request.form.get('due_date'), "%Y-%m-%d"),
            'status': request.form.get('status'),
            'assigned': request.form.getlist('assigned'),
        }

        taskID = db.devTasks.insert_one(tempDoc)
        return redirect(url_for("dev_tasks", project_id=project_id))
    

    # edit-task
    @app.route("/dev/<project_id>/edit-task/<task_id>")
    def edit_task(project_id, task_id):
        task = db.devTasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            return "Task not found", 404
        return render_template("edit_task.html", task=task, project_id=project_id)
    
    @app.route("/dev/<project_id>/edit-task/<task_id>/edit", methods=["POST"])
    def edit_task_post(project_id, task_id):
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

        return redirect(url_for("dev_tasks",project_id=project_id))

    # delete-task
    @app.route("/dev/<project_id>/tasks/<task_id>/delete", methods=["GET"])
    def delete_task_confirm(project_id, task_id):
        task = db.devTasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            return "Task not found", 404
        return render_template("delete_task_confirm.html", task=task, project_id=project_id)
    
    @app.route("/dev/<project_id>/tasks/<task_id>/delete", methods=["POST"])
    def delete_task(project_id, task_id):
        db.devTasks.delete_one({"_id": ObjectId(task_id)})
        return redirect(url_for("dev_tasks", project_id=project_id))
    

    # changes that allow comments for tasks
    @app.route("/dev/<project_id>/tasks/<task_id>/comments", methods=["GET", "POST"])
    def task_comments(project_id, task_id):
        if request.method == "POST":
            title = request.form.get("comment_title")
            comment_text = request.form.get("comment_text")
            user = session.get("username", "NONE")

            if comment_text:
                new_comment = {
                    'comment_id': str(uuid.uuid4()),
                    "title": title,
                    "text": comment_text,
                    "posted_by": user,
                    "created_at": datetime.datetime.now()
                }
                db.devTasks.update_one(
                {"_id": ObjectId(task_id)},
                {"$push": {"comments": new_comment}}
                )

            return redirect(url_for("task_comments", project_id=project_id, task_id=task_id))
        
        task = db.devTasks.find_one({"_id": ObjectId(task_id)})

        if not task:
            return "Task not found", 404
        
        return render_template("comments.html", task=task, project_id=project_id)
    
    @app.route("/dev/<project_id>/tasks/<task_id>/comments/<comment_id>/delete", methods=["GET"])
    def delete_comment_confirm(project_id, task_id, comment_id):
        task = db.devTasks.find_one({"_id": ObjectId(task_id)})
        comment_to_delete = None
        for c in task.get("comments", []):
            if c.get("comment_id") == comment_id:
                comment_to_delete = c
                break

        if not comment_to_delete:
            return "Comment not found", 404
        return render_template("delete_comment_confirm.html", project_id=project_id, task_id=task_id, comment=comment_to_delete)

    
    @app.route("/dev/<project_id>/tasks/<task_id>/comments/<comment_id>/delete", methods=["POST"])
    def delete_comment(project_id, task_id, comment_id):
        db.devTasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$pull": {"comments": {"comment_id": comment_id}}}
        )
        return redirect(url_for("task_comments", project_id=project_id, task_id=task_id))
    
    
    @app.route("/dev/<project_id>/tasks/<task_id>/comments/<comment_id>/edit", methods=["GET", "POST"])
    def edit_comment(project_id, task_id, comment_id):
        if request.method == "POST":
            updated_fields = {
                "comments.$.title": request.form.get("comment_title"),
                "comments.$.text": request.form.get("comment_text"),
            }

            db.devTasks.update_one(
            {
                "_id": ObjectId(task_id), 
                "comments.comment_id": comment_id 
            },
            {"$set": updated_fields}
            )

            return redirect(url_for("task_comments", project_id=project_id, task_id=task_id))
        
        task = db.devTasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            return "Task not found", 404
        
        comment_for_edit = None
        for c in task.get("comments", []):
            if c.get("comment_id") == comment_id:
                comment_for_edit = c
                break

        if not comment_for_edit:
            return "Comment not found", 404
    
        return render_template("edit_comment.html", project_id=project_id, task_id=task_id, comment=comment_for_edit, task=task)
    
    # end of changes for comments branch
                

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

