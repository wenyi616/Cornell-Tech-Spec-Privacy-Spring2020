import pandas as pd
import numpy as np
import collections
import sys
import os

exp_num = sys.argv[1]
unique_huge = pd.read_csv("./hugecookies/hugecookies-{}.csv".format(exp_num))

# drop nan
unique_huge.dropna(inplace=True)

unique_huge.drop(unique_huge[unique_huge.name.str.contains('Test|test|lang|SameSite|Samesite|sameSite|samesite|expires|Path|path|domain|Expires|max-age')].index, inplace=True)
unique_huge.drop(unique_huge[unique_huge.value.isin(['1','0','2','true','yes','YES','ok','nan','none','None','NO_DATA','null','setstatuscode~~1'])].index, inplace=True)

unique_huge['namevalue'] = list(map(lambda a, b: (a, b), unique_huge["name"].astype(str), unique_huge["value"].astype(str)))
temp = unique_huge.groupby(["namevalue", "context_id"], as_index = False)['time_stamp'].count()

byhost = pd.DataFrame(unique_huge.groupby(["namevalue", "context_id"], as_index = False)['host'].apply(list))
byhost.to_csv("temp.csv")

ls = pd.read_csv("temp.csv", converters={'0': eval})['0']
temp['host_list'] = list(map(lambda x: list(set(x)), ls))
temp.rename(columns={"time_stamp":"count"}, inplace=True)

if os.path.exists("temp.csv"):
    os.remove("temp.csv")

ltd = []
Counter = collections.Counter(temp.namevalue.tolist())
for key, value in Counter.items():
    if value == 1:
        ltd.append(key)

indtd = temp[temp['namevalue'].isin(ltd)].index
temp.drop(indtd, inplace=True)

temp.to_csv("./overlap-cookies/unique_namevalue-{}.csv".format(exp_num), index=False)
print("save experiment{} table done!".format(exp_num))