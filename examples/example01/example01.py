from examples.example01.workflow_factory import get_workflow

if __name__ == '__main__':
    workflow = get_workflow()
    result = workflow.run_workflow()
    for k, v in result.result_obj.items():
        print('RESULT: {}={}'.format(k, v))

# EOF