from theoktany.auth_client import *
from theoktany.client import *
from theoktany.exceptions import *
from theoktany.serializers import *

def validate(response, status_code):
    if status_code != 200:
        if 'errorCauses' in response:
            print("errrr: " + str(response['errorCauses']))
            kmsg = response['errorCauses'][0]['errorSummary']
        elif 'errorSummary' in response:
            msg = response['errorSummary']
        else:
            msg = 'Okta returned {}.'.format(status_code)
            return (False, msg)
    return response, "Yay!"