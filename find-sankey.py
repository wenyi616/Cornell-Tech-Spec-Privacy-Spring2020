import pandas as pd
import numpy as np
import collections
import math

import pandas as pd
import numpy as np
import collections
import sys
import os
import ast

exp_num = sys.argv[1]
# exp_num = 2
unique_huge = pd.read_csv("./hugecookies/hugecookies-{}.csv".format(exp_num))

# drop nan
unique_huge.dropna(inplace=True)

# ad the paper suggest, find important cookies
unique_huge = unique_huge[unique_huge['value'].str.len() >= 8]

# drop more cookies using some criteria
unique_huge.drop(unique_huge[unique_huge.name.str.contains('Test|test|lang|SameSite|Samesite|sameSite|samesite|expires|Path|path|domain|Expires|max-age')].index, inplace=True)
unique_huge.drop(unique_huge[unique_huge.value.isin(['1','0','2','true','yes','YES','ok','nan','none','None','NO_DATA','null','setstatuscode~~1'])].index, inplace=True)

# 
ls_news = ['cnn','nytimes','theguardian','washingtonpost','forbes']
ls_health = ['webmd','mayoclinic','myfitnesspal','medscape','verywellhealth']
ls_education = ['jhu','mit','edx','harvard','colledgeboard']
name_dict = {1: ls_news, 2: ls_health, 3:ls_education}
order_ls = [[1,2,3],[2,1,3],[3,1,2],[3,2,1],[1,3,2],[2,3,1]]
order = order_ls[exp_num-1]
l = name_dict[order[0]] + name_dict[order[1]] + name_dict[order[2]]

unique_huge['vname'] = unique_huge['visit_id'].apply(lambda x: l[math.ceil(x/5)-1])


# groupby 
unique_huge['namevalue'] = list(map(lambda a, b: (a, b), unique_huge["name"].astype(str), unique_huge["value"].astype(str)))
byoccur = unique_huge.groupby(["namevalue", "context_id"], as_index = False)['time_stamp'].count()

# clean host domain 
temp = list(map(lambda x:".".join(x.split(".")[:2]).replace('https://','').replace('www',''), unique_huge['host'].tolist()))                    
unique_huge['host_clean'] = temp

byhost = pd.DataFrame(unique_huge.groupby(["namevalue", "context_id"], as_index = False)['host_clean'].apply(set).reset_index(name='byhost'))
byvisit = pd.DataFrame(unique_huge.groupby(["namevalue", "context_id"], as_index = False)['vname'].apply(set).reset_index(name='byvname'))

# constrcut highlight table
highlight = pd.merge(byoccur, byhost, on=['namevalue',  'context_id'])
highlight = pd.merge(highlight, byvisit, on=['namevalue',  'context_id'])


# select only across contexts
ltd = []
Counter = collections.Counter(highlight.namevalue.tolist())
for key, value in Counter.items():
    if value == 1:
        ltd.append(key)

indtd = highlight[highlight['namevalue'].isin(ltd)].index
highlight.drop(indtd, inplace=True)

# highlight.to_csv("./visualization/sankey-helper-{}.csv".format(exp_num), index=False)

keywords = "deepintent;yahoo;advertising;ib-ibi;mookie1;atdmt;casalemedia;exelator;bttrack;doubleclick;contextweb;nr-data;pubmatic;bing;adsrvr;tapad;adsymptotic;scorecardresearch;crwdcntrl;districtm;krxd;1rx;agkn;amazon-adsystem;adentifi;adnxs;spotxchange;rubiconproject;bidr;bluekai;dnacdn;bidswitch;myvisualiq;ipredictive;quantserve;media.net;demdex;everesttech;extend.tv;facebook;openx;mathtag;mxptint;twitter;rlcdn;rkdms;owneriq;sitescout;sharethrough;simpli;taboola;3lift;myvisualiq;turn.com;adform;w55c;deepintent;yahoo;advertising;ib-ibi;mookie1;atdmt;casalemedia;exelator;bttrack;doubleclick;contextweb;nr-data;pubmatic;bing;adsrvr;tapad;adsymptotic;scorecardresearch;crwdcntrl;districtm;krxd;1rx;agkn;amazon-adsystem;adentifi;adnxs;spotxchange;rubiconproject;bidr;bluekai;dnacdn;bidswitch;myvisualiq;ipredictive;quantserve;media.net;demdex;everesttech;extend.tv;facebook;openx;mathtag;mxptint;twitter;rlcdn;rkdms;owneriq;sitescout;sharethrough;simpli;taboola;3lift;myvisualiq;turn.com;adform;w55c;zemanta"
keywords = keywords.split(";")
nv_ls = hightlight.namevalue.tolist()
origin_hosts = hightlight.byhost.tolist()
origin_web = hightlight.byvname.tolist()
contexts_ls = hightlight.context_id.tolist()

dict_ls = collections.defaultdict(set)

for i in range(1, len(nv_ls)):
    if nv_ls[i-1] != nv_ls[i]:
        continue
    u_hosts = origin_hosts[i].union(origin_hosts[i-1])
    if order.index(contexts_ls[i]) < order.index(contexts_ls[i-1]):
        in_webs = origin_web[i]
        out_webs = origin_web[i-1]
    else:
        in_webs = origin_web[i-1]
        out_webs = origin_web[i]
    for domain in keywords:
        if any(domain in string for string in u_hosts):
            for in_web in in_webs:
                for out_web in out_webs:
                    dict_ls[in_web].add((out_web, domain))

# dict_ls['forbes']