from flask import Flask
from flask import request
import json
import requests
import ssl

from config import *

app = Flask(__name__)

# Global variable to store the authentication token vCenter gives an API client to execute API calls
# (instead of having to post credentials each call)
VC_AUTH_TOKEN = ""


def authenticateToVC():
    global OTNSX_CONFIG, VC_AUTH_TOKEN
    # create a session with vCenter, which will return a session token which we can use in other API calls
    requests_url = 'https://%s/rest/com/vmware/cis/session' % (OTNSX_CONFIG['VC_HOST'])
    result = requests.post((requests_url), auth=(OTNSX_CONFIG['VC_USER'], OTNSX_CONFIG['VC_PASS']), verify=False)

    # throw an error when the return code is not 200 and the credentials are probably wrong
    if result.status_code != 200:
        raise ValueError("Authentication to vCenter failed with code %s: %s" % (result.status_code, result.text))
    else:
        json_temp = json.loads(result.text)
        # store the token in a global variable so we can use it in other functions
        VC_AUTH_TOKEN = json_temp['value']
        print("Authenticated with vCenter!")


def getVMID(vmName):
    global OTNSX_CONFIG, VC_AUTH_TOKEN

    # if we don't have an authentication token (therefor we haven't logged into vCenter yet), go get one
    if not VC_AUTH_TOKEN:
        authenticateToVC()

    # call the vSphere API to get a list of VMs and filter it by the name of the VM
    headers = {'vmware-api-session-id': VC_AUTH_TOKEN}
    result = requests.get("https://%s/rest/vcenter/vm?filter.names=%s" % (OTNSX_CONFIG['VC_HOST'], vmName), verify=False, headers=headers)

    # throw an error when the return code is not 200 and something is probably wrong
    if result.status_code != 200:
        raise ValueError("Authentication to vCenter failed with code %s - %s - %s" % (result.status_code, result.text, VC_AUTH_TOKEN))
    else:
        # example output:
        # {"value":[{"memory_size_MiB":1024,"vm":"vm-2883","name":"ansible-machine","power_state":"POWERED_OFF","cpu_count":1}]}
        # parse this json format, turn it into an array and access "value" -> first record in the returned array ([]) -> "vm" - as that is the ID we need
        json_temp = json.loads(result.text)
        vmID = json_temp['value'][0]['vm']

    return vmID


def putSecurityTag(vmID):
    global OTNSX_CONFIG
    requests_url = 'https://%s/api/2.0/services/securitytags/tag/%s/vm/%s' % (OTNSX_CONFIG['NSX_HOST'], OTNSX_CONFIG['NSX_SECURITYTAG'], vmID)
    success = requests.put((requests_url), auth=(OTNSX_CONFIG['NSX_USER'], OTNSX_CONFIG['NSX_PASS']), verify=False)
    return


def removeSecurityTag(vmID):
    global OTNSX_CONFIG
    requests_url = 'https://%s/api/2.0/services/securitytags/tag/%s/vm/%s' % (OTNSX_CONFIG['NSX_HOST'], OTNSX_CONFIG['NSX_SECURITYTAG'], vmID)
    success = requests.delete((requests_url), auth=(OTNSX_CONFIG['NSX_USER'], OTNSX_CONFIG['NSX_PASS']), verify=False)
    return


@app.route('/', methods=['POST'])
def index():
    json_temp = json.loads(request.data)
    print(json_temp['TicketID'])

    URL = '%s://%s/otrs/nph-genericinterface.pl/Webservice/GenericTicketConnectorREST/Ticket/' \
          '%s?UserLogin=%s&Password=%s&DynamicFields=True' % (
                    OTNSX_CONFIG['OTRS_PROTOCOL'],
                    OTNSX_CONFIG['OTRS_HOST'],
                    json_temp['TicketID'],
                    OTNSX_CONFIG['OTRS_USER'],
                    OTNSX_CONFIG['OTRS_PASS'])

    requestGet = requests.get(URL)

    requestJson = requestGet.json()
   
    vmNAME = requestJson['Ticket'][0]['DynamicField'][OTNSX_CONFIG['OTRS_DYNAMICFIELD']]['Value']

    vmID = getVMID(vmNAME)
    print("VM ID na de def = %s" % vmID)

    if requestJson['Ticket'][0]['Lock'] == "lock":
        putSecurityTag (vmID)
    else:
        removeSecurityTag(vmID)

    return vmID

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')
