import uuid
import hashlib
import time
import requests

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
ENDPOINT = "https://openapi.youdao.com"
PATH = "/api"
URL = ENDPOINT + PATH


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode("utf-8"))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10 : size]


class YoudaoAPI(object):
    def __init__(self, appid, appkey) -> None:
        self.appid = appid
        self.appkey = appkey

    def query(self, query, from_lang="auto", to_lang="zh-CHN"):
        curtime = str(int(time.time()))
        salt = str(uuid.uuid1())
        signStr = self.appid + truncate(query) + salt + curtime + self.appkey
        payload = {
            "q": query,
            "from": from_lang,
            "to": to_lang,
            "appKey": self.appid,
            "salt": salt,
            "signType": "v3",
            "curtime": curtime,
            "sign": encrypt(signStr),
        }
        r = requests.post(URL, params=payload, headers=HEADERS)
        result = r.json()
        return result

    def get_basic(self, query, from_lang="auto", to_lang="zh-CHN"):
        result = self.query(query, from_lang, to_lang)
        if int(result["errorCode"]) != 0:
            return "翻译失败"
        return "\n".join(result["basic"]["explains"])
