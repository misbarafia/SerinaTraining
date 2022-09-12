from requests import get, post
import time, json
import sys

sys.path.append("..")
from session.notificationsession import client as mqtt
import model


# Background task publisher
def meta_data_publisher(msg):
    try:
        mqtt.publish("notification_processor", json.dumps(msg), qos=2, retain=True)
    except Exception as e:
        pass


def get_fr_data(input_data_list, file_type, apim_key, API_version, endpoint, model_type, inv_model_id="", entityID=None,
                bg_task=None, db=None):
    print("inv_model_id: ", inv_model_id)
    output_data = []
    isComposed=False
    template=''
    try:
        for input_data in input_data_list:
            data = {}
            fr_status = 'Fail'
            fr_model_msg = "Azure get data error!"
            max_try_cnt = 5
            prebuilt_post_url = endpoint + "formrecognizer/" + API_version + "/prebuilt/invoice/analyze?includeTextDetails=true"
            custom_post_url = endpoint + \
                              "formrecognizer/%s/custom/models/%s/analyze" % (
                                  API_version, inv_model_id)
            print("prebuilt_post_url,custom_post_url: ", prebuilt_post_url, custom_post_url)

            try:
                print(" 32 azure inputcheck: ", len(input_data_list), model_type)
                cnt = 0

                cnt = cnt + 1
                max_try_cnt = 5
                fr_model_status = 0
                if model_type == "custom":
                    post_url = custom_post_url
                elif model_type == "prebuilt":
                    post_url = prebuilt_post_url
                else:
                    post_url = ""
                    fr_model_status = 0
                    fr_model_msg = "Please enter valid model type: custom/prebuilt "

                if post_url != "":
                    data = {}

                    headers = {
                        'Content-Type': file_type,
                        'Ocp-Apim-Subscription-Key': apim_key}

                    res = post(url=post_url, data=input_data,
                               headers=headers)
                    print(f"res : {res.text}")
                    fr_status = res.status_code
                    if res.status_code == 202:
                        geturl = res.headers["operation-location"]
                        print(geturl)
                        mx_try = 0
                        fr_status = "notStarted"
                        while fr_status != "succeeded":
                            resp = get(geturl, data=input_data,
                                       headers=headers)
                            # fr_status = resp.status_code
                            print(resp.status_code)
                            time.sleep(5)
                            # fr_status = resp.json['status']
                            if resp.status_code != 200:
                                print("Waiting for Form-Recogniser Response...",
                                      resp.status_code)
                                time.sleep(4)
                                mx_try = mx_try + 1
                            if mx_try == max_try_cnt:
                                fr_model_status = 1
                                fr_model_msg = "429: TooManyRequests "
                                fr_status = "429: TooManyRequests "
                                data = resp.json()
                                break
                            if 'status' in resp.json():
                                fr_status = resp.json()['status']
                                fr_model_status = 1
                                fr_model_msg = "success"

                        data = resp.json()
                        if model_type == 'custom':
                            doctype = data["analyzeResult"]["documentResults"][0]["docType"]
                            if doctype.split(":")[0] != "custom":
                                isComposed = True
                                template = doctype.split(":")[-1]
                            else:
                                isComposed = False
                                template = doctype.split(":")[-1]
                        wr_data = json.dumps(data)
                        wr_data = wr_data.replace('null', '""')
                        try:
                            cl_data = json.loads(wr_data)
                            data = cl_data

                            # if model_type == "custom":
                            #     print(len(data['analyzeResult']['documentResults'][0]['fields']['tab_1']['valueArray']))
                            #     with open('rawcust_data' + str(cnt) + '.json', 'w') as f3:
                            #         f3.write(json.dumps(data))

                        except:
                            pass
                        if mx_try < max_try_cnt:
                            if data['status'] == 'succeeded':
                                fr_status = resp.json()['status']
                                fr_model_status = 1
                                fr_model_msg = "success"

                            else:
                                fr_status = resp.json()['status']
                                fr_model_status = 0
                                fr_model_msg = resp.json()['status']
                    elif res.status_code == 400:
                        fr_model_status = 0
                        fr_model_msg = "400 (Bad Request).Failed to download image from input URL."
                        print("fr_model_msg: ", fr_model_msg)

                else:
                    fr_model_status = 0
                    fr_model_msg = "Please enter valid model type: custom/prebuilt "

                # if model_type == "custom":
                #     with open('rawcust_data.txt', 'w') as f3:
                #         f3.write(json.dumps(output_data))

            except Exception as e:
                print(e)
                fr_model_status = 0
                fr_model_msg = str(e)
                fr_status = 0
                ############ start of notification trigger #############
                # getting recipients for sending notification
                recepients = db.query(model.AccessPermission.userID).filter_by(
                    permissionDefID=1).distinct()
                recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                      model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                    model.User.isActive == 1).all()
                user_ids, *email = zip(*list(recepients))
                # just format update
                email_ids = list(zip(email[0], email[1], email[2]))
                cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                details = {"user_id": None, "trigger_code": 7016, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {"subject": "FR API Failure", "recipients": email_ids,
                                                  "endpoint_name": f"{endpoint}",
                                                  "modelID": inv_model_id}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
                data = {}
            output_data.append(data)
    except Exception as azr:
        print("Excetion in Azure call:", str(azr))
    print("output_data: ", len(output_data))
    if model_type == 'custom':
        return fr_model_status, fr_model_msg, output_data, fr_status,isComposed,template
    return fr_model_status, fr_model_msg, output_data, fr_status
