from flask import Flask
from flask import request, render_template
from examples.webapp import web_framework_factory
from examples.webapp import application_workflows
from pytaskflow.taskflow_engine import EntryPoint
import warnings


app = Flask(__name__)


@app.route('/')
def home():
    entry_point = web_framework_factory.flask_entry_point_creator(request, render_template)
    if isinstance(entry_point, EntryPoint):
        workflow = application_workflows.flask_sample_app_workflow(entry_point)
    else:
        warnings.warn("entry_point expected to be EntryPoint but is %s" % type(entry_point))
    return workflow