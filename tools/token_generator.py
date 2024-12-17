import jwt
import datetime
import os
import pytz
from tools.user import login_panel

tokenTimeExtension=300 #seconden
tokenMinute=1

SECRET_KEY = "123456789012345qQwertyuiopasdfghjklzxcvbnm67890123456789012"
def token_gnrtr(user_id):
    expiration_time = datetime.datetime.now(pytz.utc) + datetime.timedelta(minutes=tokenMinute)
    # Token içeriği (payload)
    payload = {
        "user_id": user_id,
        "exp": expiration_time.timestamp()
    }
    
    # Token oluşturma
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    os.environ["ACCESS_TOKEN"] = token
    return token


def renew_token_if_needed():
    user = None  # user değişkenini başlatıyoruz
    token = os.getenv("ACCESS_TOKEN")
    decoded_payload= None
    if not token:
        print("Token bulunamadı. Program sonlanıyor...")
        exit(1)

    try:
        # Token'i decode et ve expiration süresini kontrol et
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        exp_time = datetime.datetime.fromtimestamp(decoded_payload["exp"], pytz.utc)
        remaining_time = (exp_time - datetime.datetime.now(pytz.utc)).total_seconds()
        # UTC ile karşılaştırma
        user_id = decoded_payload["user_id"]    

    # Eğer token süresi bitmişse, programdan çık
        
        if remaining_time < 0:
            print("Token süresi dolmuş, çıkılıyor...")
            exit(1)
        # Eğer kalan süre 5 dakikadan azsa süresini uzat
        if remaining_time < tokenTimeExtension:  
            new_exp = datetime.datetime.now() + datetime.timedelta(minutes=tokenMinute)
            decoded_payload["exp"] = new_exp.timestamp()
            new_token = jwt.encode(decoded_payload, SECRET_KEY, algorithm="HS256")
            os.environ["ACCESS_TOKEN"] = new_token
        else:
            print("Token geçerli.")
    except jwt.ExpiredSignatureError:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"],options={"verify_exp": False}) 
        user_id = decoded_payload["user_id"]
        user = login_panel()
        
        if user and user["user_id"] == user_id:
            # Eğer user_id'ler eşleşiyorsa, token'ı yenileyerek devam et
            new_exp = datetime.datetime.now() + datetime.timedelta(minutes=tokenMinute)  # Yeni expiration süresi
            decoded_payload["exp"] = new_exp.timestamp()
            new_token = jwt.encode(decoded_payload, SECRET_KEY, algorithm="HS256")
            os.environ["ACCESS_TOKEN"] = new_token
            print("Token yenilendi, programa devam ediliyor.")
        else:
            # Eğer user_id'ler eşleşmiyorsa, programı sonlandır
            print("Token süresi dolmuş ve user_id eşleşmedi. Program sonlanıyor...")
            exit(1)
    except jwt.InvalidTokenError:
        print("Geçersiz token. Program sonlanıyor...")
        exit(1)

