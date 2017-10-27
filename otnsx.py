from flask import Flask
from flask import request
import json
import requests
import ssl

app = Flask(__name__)

OTNSX_CONFIG = {}
OTNSX_CONFIG['VC_HOST'] = "10.8.20.10"
OTNSX_CONFIG['VC_USER'] = "otrs@vsphere.local"
OTNSX_CONFIG['VC_PASS'] = "P@ssw0rd"

OTNSX_CONFIG['NSX_HOST'] = "10.8.20.15"
OTNSX_CONFIG['NSX_USER'] = "admin"
OTNSX_CONFIG['NSX_PASS'] = "P@ssw0rd"

OTNSX_CONFIG['NSX_SECURITYTAG'] = "securitytag-12"

VC_AUTH_TOKEN = ""

def authenticateToVC():
	global OTNSX_CONFIG, VC_AUTH_TOKEN
	requests_url = 'https://%s/rest/com/vmware/cis/session' % (OTNSX_CONFIG['VC_HOST'])
	result = requests.post((requests_url), auth=(OTNSX_CONFIG['VC_USER'], OTNSX_CONFIG['VC_PASS']), verify=False)

	if result.status_code != 200:
		raise ValueError("Authentication to vCenter failed with code %s" % (result.status_code))
	else:
		json_temp = json.loads(result.text)
		VC_AUTH_TOKEN = json_temp['value']
		print("Authenticated with vCenter!")

def getVMID(vmName):
	global OTNSX_CONFIG, VC_AUTH_TOKEN

	#if not VC_AUTH_TOKEN:
	authenticateToVC()

	headers = {'vmware-api-session-id': VC_AUTH_TOKEN}
	result = requests.get("https://%s/rest/vcenter/vm?filter.names=%s" % (OTNSX_CONFIG['VC_HOST'], vmName), verify=False, headers=headers)

	if result.status_code != 200:
		raise ValueError("Authentication to vCenter failed with code %s - %s - %s" % (result.status_code, result.text, VC_AUTH_TOKEN))
	else:
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
	print json_temp['TicketID']

	URL = 'http://192.168.178.215/otrs/nph-genericinterface.pl/Webservice/GenericTicketConnectorREST/Ticket/'
	URL += json_temp['TicketID']
	URL += '?UserLogin=sander&Password=vmware&DynamicFields=True'

	requestGet = requests.get(URL)

	requestJson = requestGet.json()

	#print rj['Ticket'][0]['Title']
	#print rj['Ticket'][0]['Lock']
	#print rj['Ticket'][0]['DynamicField'][11]['Value']
	vmNAME = requestJson['Ticket'][0]['DynamicField'][11]['Value']

	vmID = getVMID(vmNAME)
	print "VM ID na de def = %s" % vmID

	if rj['Ticket'][0]['Lock'] == "lock":
		putSecurityTag (vmID)
	else:
		removeSecurityTag (vmID)

	return vmID

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')
