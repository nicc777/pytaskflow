from .visit_counter_function import VisitCounterFunction
from .session_persistence_functions import SaveSessionFunction, GetSessionFunction
from .template_functions import ServeHomeTemplateFunction
from pytaskflow.taskflow_engine import *

visit_counter_task = Task("VisitCounterFunction", VisitCounterFunction())
get_session_task = Task("GetSessionFunction", GetSessionFunction())
save_session_task = Task("SaveSessionFunction", SaveSessionFunction())
serve_home_template_task = Task("ServeHomeTemplateFunction", ServeHomeTemplateFunction())


def sample_application_task_collection():
    collection = TaskCollection("HelloWorldApp")
    collection.add_task(get_session_task, "VisitCounterFunction", "ServeHomeTemplateFunction")
    collection.add_task(visit_counter_task, "SaveSessionFunction", "ServeHomeTemplateFunction")
    collection.add_task(save_session_task, "ServeHomeTemplateFunction", "ServeHomeTemplateFunction")
    collection.add_task(serve_home_template_task, None, None)
    return collection


# ./end of file