## Tracking across contexts experiments

------

#### Step 1: process-sql
From openWPM to data tables (cookies, js, httprequest)

> python process-sql.py

------

#### Step 2: process-cookies
Extract cookies-related information from all three tables (cookies, js, httprequest), and concatnate into a hugecookie table. 

> python process-cookies.py [exp-num] [contexts-num]

> python process-cookies.py 1 3
> python process-cookies.py 2 3
> python process-cookies.py 3 3


------

#### Step 3: Untitled
Looking for all unique combinations of (cookie name, cookie value) across contexts.
Results are in the table unique-namevalue-1/2/3.csv, in which the namevalue column describes a tuple of (cookie name, cookie value), time_stamp column describes how many counts this combination appears. These tables are pretty concise, and please refer to raw tables if needed. 

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>




#### ------ Incomplete readme notes ------
Context_id
<br>
1 | news
<br>
2 | health
<br>
3 | education