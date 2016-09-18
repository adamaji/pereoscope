import sys
import cv2
import math
import numpy as np

import requests
import json
import codecs
import subprocess

def get_stream_url(broadcast_id):
    url_to_get = "https://api.periscope.tv/api/v2/accessVideoPublic"
    payload = {"broadcast_id": broadcast_id}
    r = requests.get(url_to_get, params=payload)
    print(r.url)
    # print(r.content)
    #content = str(r.content, 'utf-8')
    content = unicode(r.content, 'utf-8')
    jsondict = json.loads(content)
    print(content)
    return jsondict['hls_url']