from flask import Flask, request
from pytaskflow.taskflow_engine import PathToTaskCollection, run_workflow, WebFrameworkEndpointFactory
from examples.example01.task_collection_factory import get_default_task_collection

app = Flask(__name__)


collection = PathToTaskCollection()
collection.register_path_processor('/', 'ServeTemplateFunction', get_default_task_collection())

endpoint_factory = WebFrameworkEndpointFactory(framework='flask')


@app.route('/')
def home():
    # Run our WorkFlow
    return run_workflow(path_to_task_collection=collection, entry_point=endpoint_factory.endpoint_creator(request))

# ./end of file
