from pytaskflow.taskflow_engine import *
from examples.example01.serve_template_function import ServeTemplateFunction


def get_default_task_collection():
    collection = TaskCollection("DefaultTaskCollection")
    collection.add_task(Task("ServeTemplateFunction", ServeTemplateFunction()), None, None)
    return collection

# EOF