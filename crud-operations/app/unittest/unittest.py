from app.main import app
from fastapi.testclient import TestClient
import logging
from datetime import datetime

logging.basicConfig(filename='unitestlog.log', encoding='utf-8', level=logging.DEBUG)
client = TestClient(app)

logging.info(f"testing of api started on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def login_test():
    body1 = {
        "username": "aroha",
        "password": "SerinaDev@202"
    }
    response1 = client.post("/apiv1.1/login", json=body1)
    body2 = {
        "username": "aroha",
        "password": "SerinaDev@2021"
    }
    response2 = client.post("/apiv1.1/login", json=body2)
    try:
        assert response1.status_code == 401
        assert response2.status_code == 200
        logging.info("login api is working")
    except:
        logging.error(f"login api failed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


login_test()

logging.info(
    f"testing completed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, please check unitestlog.log for more info")
