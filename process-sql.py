import numpy as np
import pandas as pd
import sqlite3
import sys

def get_host_from_headers(x):
    temp = x.replace('"','').split('],[')
    for t in temp:
            pair = t.replace(']]','').replace('[[','').split(',')
            if "Host" in pair:
                host_value = pair[1]
    return host_value

def get_cookies_from_headers(x):
    ls = x.replace('"','').split('],[')
    for l in ls:
        ta = l.replace(']]','').split(',')
        if "Cookie" in ta:
            return ta[-1]
    return ''

def findIdx(df, colname, keyword):
    for i, web in enumerate(df[colname].tolist()):
        if web.rfind(keyword) != -1:
            return i



for exp_number in range(1, 4):
    exp_path = "./raw-data/exp" + str(exp_number) + "/crawl-data.sqlite"

    conn = sqlite3.connect(exp_path)
    javascript_cookies = pd.read_sql_query(
        "select visit_id, record_type, change_cause, host, name, value, time_stamp from javascript_cookies;", conn)
    http_responses = pd.read_sql_query(
        "select visit_id, url, method, headers, time_stamp from http_responses where response_status == 200;", conn)
    http_requests = pd.read_sql_query("select visit_id, headers, referrer, Url, time_stamp from http_requests;", conn)
    javascript = pd.read_sql_query(
        "select visit_id, script_url, symbol, operation, value, arguments, time_stamp from javascript;", conn)
    site_visits = pd.read_sql_query("select visit_id, site_url from site_visits;", conn)

    conn.close()

    names = list(map(lambda x: x.split('.')[1], list(site_visits.site_url)))
    websites = list(names[i] for i in [0, 5, 10])

    web_dict = {
        "nytimes": 'nytimes|nyt',
        "webmd": 'webmd',
        "berkeley": 'berkeley'
    }

    indx1 = findIdx(javascript_cookies, 'host', websites[1])
    indx2 = findIdx(javascript_cookies, 'host', websites[2])
    javascript_cookies["context_id"] = [1] * (indx1)  + [2] * (indx2 - indx1) + [3] * (javascript_cookies.shape[0] - indx2)

    indx1 = findIdx(http_requests, 'url', websites[1])
    indx2 = findIdx(http_requests,'url', websites[2])
    http_requests["context_id"] = [1] * (indx1)  + [2] * (indx2 - indx1) + [3] * (http_requests.shape[0] - indx2)

    indx1 = findIdx(javascript, 'script_url', websites[1])
    indx2 = findIdx(javascript, 'script_url', websites[2])
    javascript["context_id"] = [1] * (indx1)  + [2] * (indx2 - indx1) + [3] * (javascript.shape[0] - indx2)

    for context_number in range(1,4):
        
        ############################# cookies #############################
        js_cookies = javascript_cookies[javascript_cookies.context_id == context_number]
    
        # first party cookies (filter by host)
        js_cookies_first = js_cookies[js_cookies.host.str.contains(web_dict.get(websites[context_number-1]))]

        # third party cookies (filter by host)
        js_cookies_third = js_cookies[~js_cookies.host.str.contains(web_dict.get(websites[context_number-1]))]

        js_cookies_third.to_csv('tables/' + str(exp_number)+'-'+str(context_number)+'-ThirdCookies.csv', index=False)
        
        
        ############################# JS #############################
        js = javascript[javascript.context_id == context_number]
        
        # filter by script_url (get domain from script_url)
        temp = list(map(lambda x:x[1], js['script_url'].str.split(".")))
        js['temp'] = temp
        
        js_third = js[~js.script_url.str.contains(web_dict.get(websites[context_number-1]))]

        js_third.to_csv('tables/' + str(exp_number)+'-'+str(context_number)+'-js.csv', index=False)
        
        
        ############################# HTTP REQUEST #############################
        temp = list(map(lambda x: get_host_from_headers(x), http_requests.headers.tolist()))
        http_requests["host"] = temp

        http_req_cookies = list(map(lambda x: get_cookies_from_headers(x), http_requests.headers.tolist()))
        http_requests["cookies"] = http_req_cookies

        # get domain from host (eg. "ade.googlesyndication.com" -> "googlesyndication")
        hr = http_requests[http_requests.context_id == context_number]

        temp = list(map(lambda x:x[-2], hr['host'].str.split(".")))
        hr['temp'] = temp
        
        hr_third = hr[~hr.temp.str.contains(web_dict.get(websites[context_number-1]))]

        hr_third.to_csv('tables/' + str(exp_number)+'-'+str(context_number)+'-httprequest.csv', index=False)


