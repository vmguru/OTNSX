from flask import Flask
from flask import request
import json
import requests
from pyvim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

app = Flask(__name__)

OTNSX_CONFIG = []
OTNSX_CONFIG['VC_HOST'] = "vc.lab.local"
OTNSX_CONFIG['VC_USER'] = "administrator@vsphere.local"
OTNSX_CONFIG['VC_PASS'] = "password"

OTNSX_CONFIG['NSX_HOST'] = "vc.lab.local"
OTNSX_CONFIG['NSX_USER'] = "admin"
OTNSX_CONFIG['NSX_PASS'] = "password"

OTNSX_CONFIG['NSX_SECURITYTAG'] = "securitytag-12"

def getVMID(vmNAME,vmID = 0):
	global OTNSX_CONFIG
	context = None
	if hasattr(ssl, '_create_unverified_context'):
		context = ssl._create_unverified_context()
	si = SmartConnect(host=OTNSX_CONFIG['VC_HOST'],
                     user=OTNSX_CONFIG['VC_USER'],
                     pwd=OTNSX_CONFIG['VC_PASS'],
                     port=443,
                     sslContext=context)
	content = si.RetrieveContent()

	for child in content.rootFolder.childEntity:
		if hasattr(child, 'vmFolder'):
			datacenter = child
			vmFolder = datacenter.vmFolder
			vmList = vmFolder.childEntity
			for vm in vmList:
				if hasattr(vm, 'summary') and vmID == 0:
					summary = vm.summary
					if summary.config.name == vmNAME:
						vmID = str(summary.vm)
						vmID = vmID.split(":",1)[1]
						vmID = vmID.split("'",1)[0]
				if hasattr(vm, 'childEntity') and vmID == 0:
					vmsublist = vm.childEntity
					for sub in vmsublist:
						if hasattr(sub, 'summary') and vmID == 0:
							summary = sub.summary
							if summary.config.name == vmNAME:
								vmID = str(summary.vm)
								vmID = vmID.split(":",1)[1]
								vmID = vmID.split("'",1)[0]
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

   return ''

if __name__ == '__main__':
   app.run(debug=True, host='192.168.178.19')
