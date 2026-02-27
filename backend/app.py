import pymongo
from flask import Flask, render_template, request, redirect, url_for

# def create_app():
#     app = Flask(__name__)

#     @app.route("/swdev")
#     def swdev_home():

#         docs = db.messages.find({}).sort("created_at", -1)
#         return render_template("index.html", docs=docs)

# app.create_app()
