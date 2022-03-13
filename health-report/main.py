# -*- coding: UTF-8 -*-
#!/usr/bin/env python
import requests
import logging
import sys
import json
import time
import datetime
import random

HEADERS = {
    "Connection": "keep-alive",
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "Accept-Encoding":"gzip, deflate",
}

report_data = {
    "is_grz"         : "2", # 是否接触新冠肺炎或疑似感染者
    "is_frz"         : "2", # 是否接触发热呼吸道症状患者
    "jkm_color"      : "绿码", # 健康码颜色
    "xcm_xing"       : "2",   # 行程码是否有星号
    "is_wx"          : "1",   # 是否在无锡
    "dq_province"    : "320000", # 当前所在地详细地址(省)
    "dq_city"        : "320200", # 当前所在地详细地址(市)
    "dq_area"        : "320211", # 当前所在地详细地址(区)
    "dq_address"     : "江南大学桃园19-503", # 地址
    "vehicle_number" : "",                 
    "dq_time"        : "2022-01-10 12:29:54", # 到达时间
    "stzk"           : "1",                   # 身体状况
    "other_text"     : "",                    # 身体状况为其他时填写
    "temperature"    : "2",                   # 体温
    "yszt"           : "正常", # 饮食状态       
    "xlzt"           : "好",   # 心里状态
    "qxzt[]"         : "平静", # 情绪状况
    "mqnrglzt"       : "1",   # 目前所属情况
    "is_gl"          : "1",   # 目前采取措施
    "is_whether"     : "2", # 共同居住的家庭成员有无以下情况
    "remarks"        : "",  # 备注
    "sfyd"           : "2", # 是否异动
    "ydbz"           : "",  # 异动备注
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def report(username, password) -> bool:
    logging.info("开始填报日报")
    login_data = {
        "action" : "login",
        "loginmode" : "web",
        "logintype" : "0",
        "username" : username,
        "password" : password,
        "from" : "portal",
    }
    
    r = requests.post("https://i.jiangnan.edu.cn/ssoserver/login", data=login_data, headers=HEADERS)
    cookie = requests.utils.dict_from_cookiejar(r.cookies)
    if 'CASTGC' not in cookie or 'JSESSIONID' not in cookie:
        logging.info("登录失败")
        return False
    
    auth_data = {
        "action"       : "login",
        "loginmode"    : "web",
        "username"     : username,
        "password"     : password,
        "auth"         : "9;0;3;10",
        "sign_value"   : "",
        "signfield"    : "cn",
        "personfield"  : "uid",
        "randomNumber" : "181836",
        "logintype"    : "0",
        "response_type": "code",
        "state"        : "fxt",
        "client_id"    : "fxt",
        "redirect_uri" : "http://fanxiaotong.jiangnan.edu.cn/passport/ejn",
        "display"      : "null",
        "scope"        : "scope_userinfo",
    }

    resp = requests.post("https://i.jiangnan.edu.cn/ssoserver/moc2/authorize", data=auth_data, headers=HEADERS, cookies=cookie)
    ci_session_app = {}
    for history in resp.history:
        cookie = requests.utils.dict_from_cookiejar(history.cookies)
        if "ci_session_app" in cookie:
            ci_session_app = cookie
            break

    if len(ci_session_app) == 0:
        logging.info("登录失败")
        return False

    resp = requests.post("http://fanxiaotong.jiangnan.edu.cn/daily/fill", data=report_data, headers=HEADERS, cookies=ci_session_app)
    
    if resp.status_code == 200:
        logging.info("日报填报成功")
    else:
        logging.info("日报填报结果不确定")

    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        logging.error("Usage: %s <username> <password>", sys.argv[0])
        exit(-1)

    username = sys.argv[1].strip()
    password = sys.argv[2].strip()
    random.seed(datetime.datetime.now())

    # 最多尝试5次
    for i in range(5):
        try:
            sleep_time = random.randint(100, 200)
            time.sleep(sleep_time)
            if report(username, password):
                break
        except Exception as e:
            if i == 4:
                raise e
            logging.exception(e)    
    
    