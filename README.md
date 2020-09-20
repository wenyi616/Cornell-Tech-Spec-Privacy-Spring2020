# Tracking across contexts experiments
This project aims at comparatively studying privacy violation in cross-context online tracking. We utilized [an open-source web 
privacy measurement framework](https://github.com/mozilla/OpenWPM) to collect web tracking data and wrote our own scripts to analyze the activities of web tracking.
## Context
The contexts we are interested in are news, healthcare, and education.
We index these contexts 1, 2, and 3 correspondingly.
The experiment data we used for analysis can be downloaded via [Google shared file](https://drive.google.com/drive/folders/1AmLu394ViSKfFFUMoHp6C4Fq65pdsK3j?usp=sharing).
## Step 1: Scrape data using OpenWPM scripts
Stay on each websites for 5 seconds.

Scripts: [NTP-crawl.py](NTP-crawl.py), [one-browser-demo.py](one-browser-demo.py)

## Step 2: Process sql files
From openWPM to data tables (cookies, js, httprequest)
Input [exp-num] to run all experiments up to [exp-num]

- Save crawl-data.sqlite in corresponding directory named "raw-data/exp-[exp-num]"
- The script will extract the following contents - httprequest, javascript, thirdPartyCookies
- Output csv files will be saved in directory called "tables/" and name the file in this format {exp-num}-{context-id}-{content}.csv

#### Process multiple experiments

```python process-sql.py {start-exp-num} {end-exp-num} ```

Example of processing exp-1 to exp-6 command: 

```python process-sql.py 1 6```

#### Process single experiment
```python process-sql.py {exp-num}```

Example of processing exp-1 solely

```python process-sql.py 1```

------

## Step 2: Process cookies
- Extract cookies-related information from all three tables (cookies, js, httprequest)
- Concatenate them into csv file hugecookies-{exp-num}.csv under hugecookies directory

#### Process an experiment at a time
```python process-cookies.py [exp-num]```

``` python process-cookies.py 1```

------

## Step 3: Find cookies activities across contexts
The script will read csv file from hugecookies folder.
### 3.1 Find unique cookie name value pairs
Looking for all unique combinations of (cookie name, cookie value) across contexts.
- Result saved in unique-namevalue-{exp-num}.csv
- namevalue column describes a tuple of (cookie name, cookie value)
- time_stamp column describes the occurrence of the unique cookie identifier (cookie name, cookie value)

#### Process an experiment at a time
```python find-overlap.py {exp-num}```

```python find-overlap.py 1```

### 3.2 Remove irrelevant data from hugecookies and execute weight calculation
The script removes noises from hugecookies table and calculates the unique counts (weights) from one website to another website
across contexts.
- Save an intermediate helper file in visualization sankey-helper-{exp-num}.csv
- Save weights in inout_weight_{exp-num}.csv
>- inbound: what website the cookies are sent from
>- outbound: what website the cookies go to
>- weight: the count of unique cookie domains

#### Process an experiment at a time
```python find-relation.py {exp-num}```

```python find-overlap.py 1```