##
# Script to upload a VisualSFM to Sketchfab
##
from time import sleep

# sys and argparse are included in the standard library
# requests is included with this package

import sys, os, argparse, logging, requests

# Hide the unverified https request warning
logging.captureWarnings(True)

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('path', help='path to the ply file ("%s.ply")')
parser.add_argument('-t', '--token', help='api token')
parser.add_argument('-n', '--name', help='model name, max 48 characters')
parser.add_argument('-d', '--description', help='model description, max 1024 characters')
parser.add_argument('-p', '--private', action='store_true', help='private flag (must have a Pro or Business account)')
parser.add_argument('-w', '--password', help='model password, max 64 characters (model must be private)')
parser.add_argument('--tags', help='space-separated tags')
args = parser.parse_args()

# Sketchfab URLs
SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v2/models'.format(SKETCHFAB_DOMAIN)
SKETCHFAB_MODEL_URL = 'https://{}/models/'.format(SKETCHFAB_DOMAIN)

# Upload a model
def upload(data, files):

    try:
        r = requests.post(SKETCHFAB_API_URL, data=data, files=files, verify=False)
    except requests.exceptions.RequestException as e:
        print '\nAn error occured: {}'.format(e)
        return

    result = r.json()

    if r.status_code != requests.codes.created:
        print '\nUpload failed with error: {}'.format(result)
        return

    model_uid = result['uid']
    model_url = SKETCHFAB_MODEL_URL + model_uid
    print '\nUpload successful. Your model is being processed.\n{}'.format(model_url)
 
    return model_uid

# Poll status
def poll_processing_status(model_uid):
    polling_url = '{}/{}/status?token={}'.format(SKETCHFAB_API_URL, model_uid, token)
    errors = 0
    max_errors = 10
    retry = 0
    max_retries = 50
    retry_timeout = 5  # seconds

    while (retry < max_retries) and (errors < max_errors):
        print '\nTry polling processing status (attempt #{}) ...'.format(retry)

        try:
            r = requests.get(polling_url)
        except requests.exceptions.RequestException as e:
            print '\nTry failed with error {}'.format(e)
            errors += 1
            retry += 1
            continue

        result = r.json()

        if r.status_code != requests.codes.ok:
            print '\nUpload failed with error: {}'.format(result['error'])
            errors += 1
            retry += 1
            continue

        processing_status = result['processing']
        if processing_status == 'PENDING':
            print '\nYour model is in the processing queue. Retry in {} seconds'.format(retry_timeout)
            retry += 1
            sleep(retry_timeout)
            continue
        elif processing_status == 'PROCESSING':
            print '\nYour model is being processed. Retry in {} seconds'.format(retry_timeout)
            retry += 1
            sleep(retry_timeout)
            continue
        elif processing_status == 'FAILED':
            print '\nProcessing failed: {}'.format(result['error'])
            return
        elif processing_status == 'SUCCEEDED':
            model_url = SKETCHFAB_MODEL_URL + model_uid
            print '\nProcessing successful. Check your model here: {}'.format(model_url)
            return

        retry += 1

    print 'Stopped polling after too many retries or too many errors'

##################################################
# Upload a model an poll for its processing status
##################################################
 
# Mandatory parameters
model_file = os.path.abspath(args.path)
f = open(model_file, 'rb')

files  = {
    'modelFile': f
}

token = args.token

if (type(token) is not str) or (len(token) is not 32):
    print '\n'
    parser.print_help()
    print '\n'
    sys.exit('API token is missing or invalid')

# Optional parameters
name = args.name or 'A VisualSFM Model'
if len(name) > 48:
    print '\n'
    parser.print_help()
    print '\n'
    sys.exit('Model name is too long (48) or invalid')

description = args.description or 'Model created with VisualSFM: http://ccwu.me/vsfm/'
if len(description) > 1024:
    print '\n'
    parser.print_help()
    print '\n'
    sys.exit('Model description is too long (1024) or invalid')

private = args.private
if private:
    private = 1

elif not private:
    private = 0

password = args.password or None
if private == 0:
    password = None

if (password and len(password) > 64):
    print '\n'
    parser.print_help()
    print '\n'
    sys.exit('Model password is too long (64) or invalid')

tags = args.tags
if not tags:
    tags = ''
tags += 'photogrammetry visualsfm 3dscan'  # Add some default tags

data = {
    'token': token,
    'name': name,
    'description': description,
    'tags': tags,
    'private': private,
    'password': password,
    'source': 'visualsfm'
}

try:
    model_uid = upload(data, files)
    # poll_processing_status(model_uid)
finally:
    f.close()
    print '\ndone'
