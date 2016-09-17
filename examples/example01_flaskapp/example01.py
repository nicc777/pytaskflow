from flask import Flask, request
from pytaskflow.taskflow_engine import PathToTaskCollection, run_workflow
from examples.example01.task_collection_factory import get_default_task_collection
from examples.example01.webframework_functions import register_framework_functions

app = Flask(__name__)


def prep_collections():
    collection = PathToTaskCollection()
    collection.register_path_processor('/', 'ServeTemplateFunction', get_default_task_collection())
    return collection


def prep_framework_functions():
    return register_framework_functions()


def create_endpoint(request_obj):
    web_framework = prep_framework_functions()
    endpoint_creator = web_framework.get_function('endpoint_creator')
    entry_point = endpoint_creator(request_obj)
    return entry_point


@app.route('/')
def home():
    entry_point = create_endpoint(request)
    flask_output = run_workflow(path_to_task_collection=prep_collections(), entry_point=entry_point)
    return flask_output


# ./end of file
