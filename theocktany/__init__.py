def validate(response, status_code):
    if status_code != 200:
        if 'errorCauses' in response:
            msg = response['errorCauses'][0]['errorSummary']
        elif 'errorSummary' in response:
            msg = response['errorSummary']
        else:
            msg = 'Okta returned {}.'.format(status_code)
        return (False, msg)
    return True
