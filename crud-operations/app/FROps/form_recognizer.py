import requests,time,json
def analyzeForm(url, headers, body):
    try:
        r_status = False
        while not r_status:
            r = requests.post(url, headers=headers, data=body)
            if r.status_code == 202:
                r_status = True
            elif "error" in r.json():
                print(f"{r.json()['error']['message']}")
                if "code" in r.json()["error"]:
                    if r.json()["error"]["code"] == "429":
                        split_text = f"Requests to the Analyze Invoice - Analyze Invoice Operation under Form Recognizer API (v2.1-preview.3) have exceeded rate limit of your current FormRecognizer F0 pricing tier. Please retry after "
                        sleep = int(
                            r.json()["error"]["message"]
                            .split(split_text)[1]
                            .split("second")[0]
                            .strip()
                        )
                        print(f"sleeping for {sleep} in PredictResults")
                        time.sleep(sleep)
                else:
                    print(
                        f"Error in prebuilt model status code {r.json()['error']['code']}"
                    )
                    error_type = r.json()["error"]["code"]
                    error_message = r.json()["error"]["message"]
                    raise Exception(error_type, error_message)
        geturl = r.headers["operation-location"]
        status = "notStarted"
        while status != "succeeded":
            r2 = requests.get(geturl, headers=headers)
            result = r2.json()
            if r2.status_code in (404, 500, 503):
                print(
                    f"Form Recognizer Failure :- {result['error']['message']}"
                )
                error_type = result["error"]["code"]
                error_message = result["error"]["message"]
                raise Exception(error_type, error_message)
            if r2.status_code == 200:
                if result["status"] == "failed":
                    print(
                        f"Form Recognizer Failure :- {result['analyzeResult']['errors'][0]['message']}"
                    )
                    error_type = result["analyzeResult"]["errors"][0]["code"]
                    error_message = result["analyzeResult"]["errors"][0]["message"]
                    raise Exception(error_type, error_message)
                else:
                    status = result["status"]
            else:
                if result["error"]["code"] == "429":
                    split_text = "Requests to the Analyze Invoice - Get Analyze Invoice Result Operation under Form Recognizer API (v2.1-preview.3) have exceeded rate limit of your current FormRecognizer F0 pricing tier. Please retry after "
                    sleep = int(
                        result["error"]["message"]
                        .split(split_text)[1]
                        .split("second")[0]
                        .strip()
                    )
                    print(f"sleeping for {sleep} in GetResults")
                    time.sleep(sleep)
                else:
                    raise Exception("Unknown Error", r2.content)
            if status == "running":
                time.sleep(5)
        return result
    except Exception as e:
        print(f"{e}")
        return {"message":f"exception {e}"}

def getModelResponse(get_url, headers):
    status_code = False
    ntry = 0
    resp_json = {}
    message = "failure"
    while not status_code:
        try:
            resp = requests.get(url=get_url, headers=headers)
            if resp.status_code == 200:
                resp_json = resp.json()
                model_status = resp_json["modelInfo"]["status"]
                if model_status == "ready":
                    status_code = True
                    message = "success"
                else:
                    status_code = False
            
            time.sleep(3)
            ntry += 1
            if ntry >= 15:
                message = "failure"
                status_code = True
        except Exception as e:
            message ="exception"
            
    return {"message":message, "result":resp_json}