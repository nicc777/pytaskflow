from pytaskflow.taskflow_engine import EntryPoint, Result, WebFramework, LoggingHandler
from flask import render_template, make_response, redirect


def flask_actions(action='RenderTemplate', context=None, template_name='index.html', redirect_url='/', cookies=None):
    if not isinstance(cookies, dict):
        cookies = None
    if action == 'RenderTemplate':
        if context is not None:
            response = make_response(render_template(template_name, context=context))
        else:
            response = make_response(render_template(template_name))
    else:
        response = make_response(redirect(redirect_url))
    if cookies is not None:
        for key, value in cookies.items():
            response.set_cookie(key, value)
    return response


def process_result(result=Result(None), entry_point=EntryPoint()):
    result_obj = result.result_obj
    if 'WebFramework' in entry_point.other_instructions:
        if entry_point.other_instructions['WebFramework'] == 'flask':
            if result_obj['Action'] == 'Redirect':
                return flask_actions(action='Redirect', context=None, template_name='', redirect_url=result_obj['RedirectURL'], cookies=entry_point.cookies)
            else:
                return flask_actions(action='RenderTemplate', context=result_obj, template_name=result_obj['TemplateName'], redirect_url='', cookies=entry_point.cookies)
    raise Exception("Cannot process web framework result")


def endpoint_creator(request_obj, other_objs={}, other_instructions={}):
    other_instructions['WebFramework'] = 'flask'
    entry_point = EntryPoint(
        request_path=request_obj.path,
        request_method=request_obj.method,
        query_string=request_obj.args,
        post_data=request_obj.form,
        cookies=request_obj.cookies,
        default_template='index.html',
        log_handler=LoggingHandler(),
        framework_request_obj=request_obj,
        framework_response_obj=None,
        additional_framework_objects=other_objs,
        other_instructions=other_instructions,
    )
    return entry_point


def register_framework_functions():
    framework_functions = WebFramework('flask')
    framework_functions.register_framework_function(process_result)
    framework_functions.register_framework_function(endpoint_creator)
    return framework_functions

# EOF