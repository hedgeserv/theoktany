def validate(response, status_code):
    if status_code in [200, 201, 202, 204]:
        return response, "Success"

    if response.get('errorCauses'):
        message = response['errorCauses'][0]['errorSummary']
    elif response.get('errorSummary'):
        message = response['errorSummary']
    else:
        message = 'Okta returned {}.'.format(status_code)

    return False, message