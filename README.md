# Tracking across contexts experiments


#### Step 1: process-sql
From openWPM to data tables (cookies, js, httprequest)

> python process-sql.py [exp-num] 
<br>
> python process-sql.py 1

------

#### Step 2: process-cookies
Extract cookies-related information from all three tables (cookies, js, httprequest), and concatnate into a hugecookie table. 

> python process-cookies.py [exp-num]
<br>
> python process-cookies.py 1
<br>
> python process-cookies.py 2
<br>
> python process-cookies.py 3


------

#### Step 3: find-cookies-across-contexts
Looking for all unique combinations of (cookie name, cookie value) across contexts.
Results are in the table unique-namevalue-1/2/3.csv, in which the namevalue column describes a tuple of (cookie name, cookie value), time_stamp column describes how many counts this combination appears. These tables are pretty concise, and please refer to raw tables if needed. 

<br>
<br>
<br>
<br>
<br>
<br>





#### ------ Some random notes ------
Context_id

1 | news

2 | health

3 | education

//

Go scale: each exp runs too long (1hr) -> change to 5s (instead of 20s) for each page

//
