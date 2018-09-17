import json
import requests
import jenkins

r = requests.get('http://platform-jenkins.zenoss.eng/job/product-assembly/job/develop/job/resmgr-pipeline/114/')
if r.ok:
    content = json.loads(r.text or r.content)
    print(content)


