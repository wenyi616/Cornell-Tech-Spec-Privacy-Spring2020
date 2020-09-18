import numpy as np
import pandas as pd
import math
import sys


def extract_from_jscookies(cookies):
    set_cookies = cookies[["context_id", "visit_id", "host", "name", "value", "time_stamp", "record_type"]]

    # set cookies
    set_cookies.rename(columns={"record_type": "type"}, inplace=True)
    set_cookies.fillna({'type': "set"}, inplace=True)
    return set_cookies

def sep_cookies(ls):
    res = []
    for l in ls:
        idx = l.find('=')
        if idx > 0:
            res.append((l[:idx], l[idx+1:]))
    return res

def extract_from_js(js):
    js_cookies = js[js.symbol == 'window.document.cookie']
    js_cookies = js_cookies[js_cookies.value.notnull()]
    js_cookies_list = list(map(lambda x:x.replace(" ","").split(';'), js_cookies.value.tolist()))
    js_cookies_ls_dict = list(map(lambda x:sep_cookies(x), js_cookies_list))

    js_cookies['cookies_dict'] = js_cookies_ls_dict

    js_cookies_temp = js_cookies[['context_id','visit_id', 'script_url', 'cookies_dict', "time_stamp", "operation"]]

    ids = []
    vids = []
    hosts = []
    c_names = []
    c_values = []
    t_stamps = []
    types = []
    for _, row in js_cookies_temp.iterrows():
        Id = row.context_id
        vid = row.visit_id
        host = row.script_url
        for name, value in row.cookies_dict:
            ids.append(Id)
            vids.append(vid)
            hosts.append(host)
            c_names.append(name)
            c_values.append(value)
            t_stamps.append(row.time_stamp)
            types.append(row.operation)

    js_cookies_new = pd.DataFrame({"context_id":ids, "visit_id":vids, "host": hosts, "name":c_names, "value":c_values, "time_stamp":t_stamps, "type":types})

    # cookie use tables
    js_cookies_new.fillna({'type':"use"}, inplace=True)
    return js_cookies_new

def extract_http(httprequests):
    httprequests = httprequests[httprequests.cookies.notnull()]

    ids = []
    vids = []
    hosts = []
    c_names = []
    c_values = []
    t_stamps = []
    for i, row in httprequests.iterrows():
        Id = row.context_id
        vid = row.visit_id
        cookies_ls = row.cookies.replace(' ','').split(';')
        for l in cookies_ls:
            idx = l.find('=')
            if idx > 0:
                ids.append(row.context_id)
                vids.append(vid)
                hosts.append(row.host)
                c_names.append(l[:idx])
                c_values.append(l[idx+1:])
                t_stamps.append(row.time_stamp)

    httpcookies = pd.DataFrame({"context_id":ids, "visit_id": vids, "host": hosts, "name":c_names, "value":c_values, "time_stamp":t_stamps})
    httpcookies["type"] = ["sent"] * httpcookies.shape[0]

    return httpcookies

def merge_cookies(jsc_cookies, js_cookies, http_cookies):
    bigcookies = pd.concat([jsc_cookies, js_cookies, http_cookies], ignore_index=True)
    return bigcookies

if __name__ == '__main__':
    experiment_num = sys.argv[1] #1
    web_nums = 3

    # cookies (set/change httpresponce, js)
    bigcookies = []

    for i in range(1, int(web_nums) + 1):
        cookies = pd.read_csv("./tables/{}-{}-ThirdCookies.csv".format(experiment_num, i))
        jscookiesc = extract_from_jscookies(cookies)
        httprequests = pd.read_csv("./tables/{}-{}-httprequest.csv".format(experiment_num, i))
        httpc = extract_http(httprequests)
        js = pd.read_csv("./tables/{}-{}-js.csv".format(experiment_num, i))
        jsc = extract_from_js(js)
        bigcookies.append(merge_cookies(jscookiesc, httpc, jsc))

    print("--------concatenate bigcookies--------")
    hugecookies = pd.concat(bigcookies)

    print("--------save hugecookies--------")
    hugecookies.to_csv("./hugecookies/hugecookies-{}.csv".format(experiment_num), index=False)
    # unique_hugecookies = hugecookies.drop_duplicates()
    # unique_hugecookies.to_csv("./hugecookies/unique_hugecookies-{}.csv".format(experiment_num), index=False)