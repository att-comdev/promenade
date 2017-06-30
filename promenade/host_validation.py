from . import *
import os subprocess
import requests
import logger


#Validate Kubelet is running without error
def check_k8s():
    pass
#Validate the Promenade files match the SHA Hashes
def validate_sha():
    pass

#Validate Kubernetes API Response
def validate_api():
    api_request_external = requests.get('http://localhost:8080')
    if api_request.status_code == 200:
        log.info("K8's External API API is responding")
    else:
        log.debug("K8's API is not responding")
    #TODO: Figure out a way to get the internal API Request IP
    #api_request_internal = request.get('http://')
