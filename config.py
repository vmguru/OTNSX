# This is the configuration file for OTNSX.py
OTNSX_CONFIG = {
    'VC_HOST': "vcenter",                   # vCenter credentials
    'VC_USER': "otrs@vsphere.local",
    'VC_PASS': "P@ssw0rd",
    'NSX_HOST': "nsx-manager",              # NSX Manager credentials
    'NSX_USER': "admin",
    'NSX_PASS': "P@ssw0rd",
    'NSX_SECURITYTAG': "securitytag-12",    # The NSX Security Tag we're tagging and untagging VMs with
    'OTRS_PROTOCOL': 'http',                # or https
    'OTRS_HOST': '192.168.178.215',         # OTRS Host containing the ticket
    'OTRS_USER': 'sander',
    'OTRS_PASS': 'vmware',
    'OTRS_DYNAMICFIELD': 11                 # Which dynamic field to read for the virtual machine
}