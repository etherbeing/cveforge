# FIXME with the content of here: https://cwe.mitre.org/data/downloads.html
import json
import logging
import re
import requests

BASE_URL = "https://cse.google.com/cse/element/v1"
params: dict[str, str] = {
}
REGEX = re.compile(r'google\.search\.cse\.api\d+\(\s*(\{.*?\})\s*\)', re.DOTALL)

def consult(query: str):
    result: dict[str, str] = {}
    params["q"] = query
    response = requests.get(BASE_URL, params=params, timeout=10)
    if not response.ok:
        logging.warning("Response is not ok, reason %s", response.status_code)
        return result
    # response is JSONP, need to strip the callback
    match = REGEX.search(response.text)
    if match:
        obj = json.loads(match.group(1))
        print(obj)
        result = json.loads(obj)
    return result