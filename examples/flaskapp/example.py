from flask import Flask
from flask import request, render_template, redirect, make_response
from examples.webapp import web_framework_factory
from examples.webapp import application_workflows
from pytaskflow.taskflow_engine import EntryPoint
import warnings


app = Flask(__name__)


@app.route('/')
def home():
    # Set the default
    workflow = render_template("base.html", visits=0)
    # Set-up our EntryPoint
    other_objects = {
        'redirect': redirect,
        'make_response': make_response
    }
    entry_point = web_framework_factory.flask_entry_point_creator(request_obj=request, response_obj=render_template, other_objs=other_objects)
    # Run our WorkFlow
    if isinstance(entry_point, EntryPoint):
        workflow = application_workflows.flask_sample_app_workflow(entry_point)
    else:
        warnings.warn("entry_point expected to be EntryPoint but is %s" % type(entry_point))
    return workflow

# ./end of file
