__author__ = 'Sun Fei'

import json
import requests
import parameter
import config
from loginform import fill_login_form
from form import Form
from pprint import pprint

negKeywords = config.negKeywords

def checkStringContainKey(testString,keyWords):
    for word in negKeywords:

        if word in testString:
            return True   
    return False

#pprint(checkStringContainKey(testString,negKeywords))

with open('phase1.json') as data_file:
    data = json.load(data_file)

    #pprint(data)

    client = requests.Session()
    start_urls = parameter.login_urls
    login_user = parameter.username
    login_pass = parameter.password

    response = client.get(start_urls[0],verify=False)
    args, url, method = fill_login_form(response.url, response.content, login_user, login_pass)

    loginResponse = client.post(url, data=args, headers=dict(Referer=start_urls))
    pprint(loginResponse)
    jsonform = []
    if "ERROR: Invalid username" in response.content:
        pprint("Login failed")
    else: 
        pprint("login successful")

        for formDetails in data:

            url = formDetails["url"]
            action = formDetails["action"]
            if checkStringContainKey(action,negKeywords)==False:#check the Negative keywords to filter out non-sensitive data
                if formDetails["method"].lower() == "get":# form is a get form, it cannot 
                    pprint("get")
                    #we send a request with randomly filled in token
                    csrfForm = Form(url,formDetails)
                    pprint(csrfForm)
                    valid_parameters = dict(csrfForm.fill_entries())
                    pprint(valid_parameters)

                    try:
                        r = client.get(action,params=urlencode(valid_parameters))
                        if r != None:
                            if r.status_code == 200:
                                #formDetails["url"] = url 
                                jsonform.append(formDetails)
                                #pprint("post form "+csrfForm.formdata["action"] +  " is vulnerable to CSRF")
                        continue
                    except :
                        pprint("anti-csrf")

                elif formDetails["method"].lower() == "post":# form is a post form, check for CSRF
                    csrfForm = Form(url,formDetails)
                    #we send a request with randomly filled in token
                    valid_parameters = dict(csrfForm.fill_entries())
                    try:
                        r = client.post(action,valid_parameters)
                        if r != None:#sometimes the request can not be processed
                            if r.status_code == 200:#  reponse 200 means the CSRF is successful
                                #formDetails["url"] = url 
                                jsonform.append(formDetails)
                        continue
                    except :
                        pprint("anti-csrf")

with open("phase3.json",'w') as outfile:
    json.dump(jsonform,outfile,indent=4)