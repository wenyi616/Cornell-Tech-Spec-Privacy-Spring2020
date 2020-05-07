import pandas as pd
import numpy as np
import collections
import sys
import os

exp_num = sys.argv[1]
unique_huge = pd.read_csv("./hugecookies/hugecookies-{}.csv".format(exp_num))

# drop nan
unique_huge.dropna(inplace=True)

# ad the paper suggest, find important cookies
unique_huge = unique_huge[unique_huge['value'].str.len() >= 8]

# drop more cookies using some criteria
unique_huge.drop(unique_huge[unique_huge.name.str.contains('Test|test|lang|SameSite|Samesite|sameSite|samesite|expires|Path|path|domain|Expires|max-age')].index, inplace=True)
unique_huge.drop(unique_huge[unique_huge.value.isin(['1','0','2','true','yes','YES','ok','nan','none','None','NO_DATA','null','setstatuscode~~1'])].index, inplace=True)

# groupby 
unique_huge['namevalue'] = list(map(lambda a, b: (a, b), unique_huge["name"].astype(str), unique_huge["value"].astype(str)))
byoccur = unique_huge.groupby(["namevalue", "context_id"], as_index = False)['time_stamp'].count()

# clean host domain 
temp = list(map(lambda x:".".join(x.split(".")[:2]).replace('https://','').replace('www',''), unique_huge['host'].tolist()))                    
unique_huge['host_clean'] = temp

byhost = pd.DataFrame(unique_huge.groupby(["namevalue", "context_id"], as_index = False)['host_clean'].apply(set).reset_index(name='byhost'))

# constrcut highlight table
highlight = pd.merge(byoccur, byhost, on=['namevalue',  'context_id'])


# select only across contexts
ltd = []
Counter = collections.Counter(highlight.namevalue.tolist())
for key, value in Counter.items():
    if value == 1:
        ltd.append(key)

indtd = highlight[highlight['namevalue'].isin(ltd)].index
highlight.drop(indtd, inplace=True)

highlight.to_csv("./overlap-cookies/unique_namevalue-{}.csv".format(exp_num), index=False)