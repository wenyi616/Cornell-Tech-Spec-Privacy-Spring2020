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

    for context_number in range(0, 3):
        ############################# cookies #############################
        js_cookies = javascript_cookies[
            javascript_cookies.visit_id.isin(range(context_number * 5 + 1, context_number * 5 + 6))]

        # first party cookies (filter by host)
        js_cookies_first = js_cookies[js_cookies.host.str.contains(web_dict.get(websites[context_number]))]

        # third party cookies (filter by host)
        js_cookies_third = js_cookies[~js_cookies.host.str.contains(web_dict.get(websites[context_number]))]

        # js_cookies_first.to_csv('1-'+str(context_number+1)+'-FirstCookies.csv', index=False)

        js_cookies_third['context_id'] = context_number + 1
        js_cookies_third.to_csv('tables/' + str(exp_number) + '-' + str(context_number + 1) + '-ThirdCookies.csv', index=False)

        ############################# JS #############################
        js = javascript[javascript.visit_id.isin(range(context_number * 5 + 1, context_number * 5 + 6))]

        # filter by script_url (get domain from script_url)
        temp = list(map(lambda x: x[1], js['script_url'].str.split(".")))
        js['temp'] = temp

        js_third = js[~js.script_url.str.contains(web_dict.get(websites[context_number]))]

        js_third['context_id'] = context_number + 1
        js_third.to_csv('tables/' + str(exp_number) + '-' + str(context_number + 1) + '-js.csv', index=False)

        ############################# HTTP REQUEST #############################
        temp = list(map(lambda x: get_host_from_headers(x), http_requests.headers.tolist()))
        http_requests["host"] = temp

        http_req_cookies = list(map(lambda x: get_cookies_from_headers(x), http_requests.headers.tolist()))
        http_requests["cookies"] = http_req_cookies

        # get domain from host (eg. "ade.googlesyndication.com" -> "googlesyndication")
        hr = http_requests[http_requests.visit_id.isin(range(context_number * 5 + 1, context_number * 5 + 6))]

        temp = list(map(lambda x: x[-2], hr['host'].str.split(".")))
        hr['temp'] = temp

        hr_third = hr[~hr.temp.str.contains(web_dict.get(websites[context_number]))]

        hr_third['context_id'] = context_number + 1
        hr_third.to_csv('tables/' + str(exp_number) + '-' + str(context_number + 1) + '-httprequest.csv', index=False)



