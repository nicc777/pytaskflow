from pytaskflow.taskflow_engine import *
import uuid


def get_session_id(entry_point):
    if isinstance(entry_point, EntryPoint):
        if entry_point.cookies is not None:
            if 'SESSIONID' in entry_point.cookies:
                return entry_point.cookies['SESSIONID']
            elif 'SESSION_ID' in entry_point.cookies:
                return entry_point.cookies['SESSION_ID']
        if entry_point.query_string is not None:
            if 'SESSIONID' in entry_point.query_string:
                return entry_point.query_string['SESSIONID']
            elif 'SESSION_ID' in entry_point.query_string:
                return entry_point.query_string['SESSION_ID']
    return None


class SaveSessionFunction(Function):
    def __init__(self):
        super(SaveSessionFunction, self).__init__()

    def result(self, entry_point=EntryPoint(), previous_result=None):
        session_token = get_session_id(entry_point)
        session_data = None
        if session_token is not None:
            if previous_result is not None:
                if isinstance(previous_result, Result):
                    session_data = previous_result.result_obj
                    p = FileBasedSessionPersistence(session_token, session_data)
                    p.save_session_data()
        result = Result({'SessionToken': session_token, 'Proceed': True, 'SessionData': session_data})
        return result


class GetSessionFunction(Function):
    def __init__(self):
        super(GetSessionFunction, self).__init__()

    def result(self, entry_point=EntryPoint(), previous_result=None):
        session_token = get_session_id(entry_point)
        session_data = None
        if session_token is not None:
            p = FileBasedSessionPersistence(session_token, session_data)
            session_data = p.get_session_data()
            result = Result({'SessionToken': session_token, 'Proceed': True, 'SessionData': session_data})
            return result
        return Result({'SessionToken': uuid.uuid4().hex, 'Proceed': True, 'SessionData': None})

# ./end of file