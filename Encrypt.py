from cryptography.fernet import Fernet
import datetime

def generate_token(key="BInT5jLb8KGkXGNPWpuUdzhdfMeK320rMiZdHDPLaVY="):
    fernet_obj=Fernet(key.encode("ascii"))
    today=str(datetime.date.today()).encode()
    token=fernet_obj.encrypt(today)
    return token.decode()


print(generate_token())