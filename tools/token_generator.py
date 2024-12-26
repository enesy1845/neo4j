# tools/token_generator.py
import jwt
import datetime
import os
import pytz
from tools.user import login_panel
from tools.database import get_db

tokenTimeExtension = 300  # saniye
tokenMinute = 1
SECRET_KEY = "123456789012345qQwertyuiopasdfghjklzxcvbnm67890123456789012"

def token_gnrtr(user_id):
    expiration_time = datetime.datetime.now(pytz.utc) + datetime.timedelta(minutes=tokenMinute)
    payload = {
        "user_id": str(user_id),
        "exp": expiration_time.timestamp()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    os.environ["ACCESS_TOKEN"] = token
    return token

def renew_token_if_needed():
    token = os.getenv("ACCESS_TOKEN")
    if not token:
        print("Token bulunamadı. Program sonlanıyor...")
        exit(1)
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        exp_time = datetime.datetime.fromtimestamp(decoded_payload["exp"], pytz.utc)
        remaining_time = (exp_time - datetime.datetime.now(pytz.utc)).total_seconds()
        user_id = decoded_payload["user_id"]

        if remaining_time < 0:
            print("Token süresi dolmuş, çıkılıyor...")
            exit(1)

        if remaining_time < tokenTimeExtension:
            new_exp = datetime.datetime.now() + datetime.timedelta(minutes=tokenMinute)
            decoded_payload["exp"] = new_exp.timestamp()
            new_token = jwt.encode(decoded_payload, SECRET_KEY, algorithm="HS256")
            os.environ["ACCESS_TOKEN"] = new_token
        else:
            print("Token geçerli.")

    except jwt.ExpiredSignatureError:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        user_id = decoded_payload["user_id"]
        with next(get_db()) as db:
            user = login_panel(db)
            if user and str(user.user_id) == user_id:
                new_exp = datetime.datetime.now() + datetime.timedelta(minutes=tokenMinute)
                decoded_payload["exp"] = new_exp.timestamp()
                new_token = jwt.encode(decoded_payload, SECRET_KEY, algorithm="HS256")
                os.environ["ACCESS_TOKEN"] = new_token
                print("Token yenilendi, programa devam ediliyor.")
            else:
                print("Token süresi dolmuş ve user_id eşleşmedi. Program sonlanıyor...")
                exit(1)
    except jwt.InvalidTokenError:
        print("Geçersiz token. Program sonlanıyor...")
        exit(1)
