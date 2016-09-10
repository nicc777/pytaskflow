from flask import Flask
from flask import request
from pytaskflow.taskflow_engine import EntryPoint, LoggingHandler
import warnings
import inspect
from examples.example01.workflow_factory import workflow_from_path

app = Flask(__name__)


def entry_point_creator(other_objs={}, other_instructions={}):
    try:
        _flask = __import__('flask', globals(), locals(), ['request'], 0)
        if not (inspect.ismodule(_flask) and _flask.__name__ == 'flask'):
            warnings.warn("It doesn't appear that flask is installed, so this function will not be able to construct an EntryPoint")
        else:
            other_instructions['WebFramework'] = 'flask'
            entry_point = EntryPoint(
                request_path=request.path,
                request_method=request.method,
                query_string=request.args,
                post_data=request.form,
                cookies=request.cookies,
                default_template='index.html',
                log_handler=LoggingHandler(),
                framework_request_obj=request,
                framework_response_obj=None,
                additional_framework_objects=other_objs,
                other_instructions=other_instructions,
            )
            return entry_point
    except:
        warnings.warn("It appears flask is not installed. Your app will now probably break...")
    return EntryPoint()


@app.route('/')
def home():
    # Run our WorkFlow
    return workflow_from_path(entry_point_creator())

# ./end of file