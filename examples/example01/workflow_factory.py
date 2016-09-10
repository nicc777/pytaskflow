from pytaskflow.taskflow_engine import WebFrameworkResult
from examples.example01.task_collection_factory import *
from pytaskflow.framework_factory import flask_actions
import warnings, types

PATH_BASED_TASK_COLLECTIONS = {
    # PATH, ( FIRST_TASK_NAME, TASK_COLLECTION ),
    '/': ('ServeTemplateFunction', get_default_task_collection()),
}
DEFAULT_TASK_COLLECTION = get_default_task_collection()
DEFAULT_FIRST_TASK_NAME = 'ServeTemplateFunction'

framework_processor = WebFrameworkResult(framework='flask')


def workflow_from_path(entry_point):
    template_name = 'index.html'
    action = 'ServeTemplate'
    redirect_url = '/'
    task_collection = DEFAULT_TASK_COLLECTION
    first_task_name = DEFAULT_FIRST_TASK_NAME
    result_obj = {}
    result = Result(None)
    if isinstance(entry_point, EntryPoint):
        if entry_point.request_path in PATH_BASED_TASK_COLLECTIONS:
            task_collection = PATH_BASED_TASK_COLLECTIONS[entry_point.request_path][1]
            first_task_name = PATH_BASED_TASK_COLLECTIONS[entry_point.request_path][0]
        app_workflow = WorkFlow(first_task_name, task_collection, entry_point=entry_point)
        result = app_workflow.result
        if isinstance(result, Result):
            result_obj = result.result_obj
            if 'Action' in result_obj:
                if result_obj['Action'] == 'Redirect':
                    if 'RedirectURL' in result_obj:
                        redirect_url = result_obj['RedirectURL']
            else:
                result_obj = {
                    'Action': 'Redirect',
                    'RedirectURL': '/',
                }
            if 'TemplateName' in result_obj:
                template_name = result_obj['TemplateName']
        else:
            warnings.warn("result was expected to be Result() but is %s" % type(result))
            result_obj = {
                'Action': 'Redirect',
                'RedirectURL': '/',
            }
    else:
        result_obj = {
            'Action': 'Redirect',
            'RedirectURL': '/',
        }
        entry_point = EntryPoint()
    result.result_obj = result_obj
    return framework_processor.process_result(result=result, entry_point=entry_point)

# EOF
