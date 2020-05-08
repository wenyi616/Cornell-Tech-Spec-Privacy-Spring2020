import numpy as np
import pandas as pd
import sqlite3
import sys
import os

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


for exp_number in range(1, int(sys.argv[1]) + 1):
    exp_path = "./raw-data/5-1-exp"+str(exp_number)+"/crawl-data.sqlite"
    
    if not os.path.exists(exp_path):
        continue
    conn = sqlite3.connect(exp_path)
    javascript_cookies = pd.read_sql_query("select visit_id, record_type, change_cause, host, name, value, time_stamp from javascript_cookies;", conn)
    http_requests = pd.read_sql_query("select visit_id, headers, referrer, Url, top_level_url, time_stamp from http_requests;", conn)
    javascript = pd.read_sql_query("select visit_id, script_url, top_level_url, symbol, operation, value, arguments, time_stamp from javascript;", conn)
    site_visits = pd.read_sql_query("select visit_id, site_url from site_visits;", conn)
    
    conn.close()

    names = list(map(lambda x: x.split('.')[1], list(site_visits.site_url)))
    first_context = list( names[i] for i in [0,25,50])
    websites = list( name for name in names[::5])

    web_dict = {
        'cnn':'cnn',
        'nytimes':'nytimes|nyt',
        'theguardian':'theguardian',
        'washingtonpost':'washingtonpost',
        'forbes':'forbes',
        'webmd':'webmd',
        'mayoclinic':'mayoclinic',
        'myfitnesspal':'myfitnesspal',
        'medscape':'medscape',
        'verywellhealth':'verywellhealth',
        'jhu':'jhu',
        'mit':'mit',
        'edx':'edx',
        'harvard':'harvard',
        'collegeboard':'collegeboard'
    }

    firstparty_dict = {
        1 : 'cnn|nytimes|nyt|theguardian|washingtonpost|forbes',
        2 : 'webmd|mayoclinic|myfitnesspal|medscape|verywellhealth',
        3 : 'jhu|mit|edx|harvard|collegeboard'
    }

    context_dict = {
        "cnn": 1,
        "webmd": 2,
        "jhu": 3
    }

    # fix leftover issue (context_id)
    indx1 = findIdx(javascript_cookies, 'host', first_context[1])
    indx2 = findIdx(javascript_cookies, 'host', first_context[2])
    javascript_cookies["context_id"] = [context_dict[first_context[0]]] * (indx1) + [context_dict[first_context[1]]] * (indx2 - indx1) + [context_dict[first_context[2]]] * (javascript_cookies.shape[0] - indx2)

    indx1 = findIdx(http_requests, 'top_level_url', first_context[1])
    indx2 = findIdx(http_requests,'top_level_url', first_context[2])
    http_requests["context_id"] = [context_dict[first_context[0]]] * (indx1) + [context_dict[first_context[1]]] * (indx2 - indx1) + [context_dict[first_context[2]]] * (http_requests.shape[0] - indx2)

    indx1 = findIdx(javascript, 'top_level_url', first_context[1])
    indx2 = findIdx(javascript, 'top_level_url', first_context[2])
    javascript["context_id"] = [context_dict[first_context[0]]] * (indx1) + [context_dict[first_context[1]]] * (indx2 - indx1) + [context_dict[first_context[2]]] * (javascript.shape[0] - indx2)


    for context_number in range(1,4):
        
        ############################# cookies #############################
        js_cookies = javascript_cookies[javascript_cookies.context_id == context_number]
    
        # first party cookies (filter by host)
        js_cookies_first = js_cookies[js_cookies.host.str.contains(firstparty_dict[context_number])]

        # third party cookies (filter by host)
        js_cookies_third = js_cookies[~js_cookies.host.str.contains(firstparty_dict[context_number])]

        js_cookies_third.to_csv('tables/' + str(exp_number) + '-' + str(context_number) + '-ThirdCookies.csv', index=False)
        
        
        ############################# JS #############################
        js = javascript[javascript.context_id == context_number]
        
        # script_url might be empty
        js.drop(js[js['script_url'] == ''].index, inplace = True)
        
        # filter by script_url (get domain from script_url)
        temp = list(map(lambda x:".".join(x.split(".")[:2]).replace('https://','').replace('www',''), js['script_url'].tolist()))                    
        js['script_domain'] = temp
        
        js_third = js[~js.script_url.str.contains(firstparty_dict[context_number])]

        js_third.to_csv('tables/' + str(exp_number) + '-' + str(context_number) + '-js.csv', index=False)
        
        
        ############################# HTTP REQUEST #############################
        temp = list(map(lambda x: get_host_from_headers(x), http_requests.headers.tolist()))
        http_requests["host"] = temp

        http_req_cookies = list(map(lambda x: get_cookies_from_headers(x), http_requests.headers.tolist()))
        http_requests["cookies"] = http_req_cookies

        # get domain from host (eg. "ade.googlesyndication.com" -> "googlesyndication")
        hr = http_requests[http_requests.context_id == context_number]

        hr.drop(hr[hr['host'] == ''].index, inplace = True)
        temp = list(map(lambda x:x.split(".")[-2] if len(x.split(".")) > 1 else x, hr['host'].tolist()))
        
        hr['host_domain'] = temp
        
        hr_third = hr[~hr.host_domain.str.contains(firstparty_dict[context_number])]

        hr_third.to_csv('tables/' + str(exp_number) + '-' + str(context_number) + '-httprequest.csv', index=False)

        print('context-'+str(context_number)+ "[done]")