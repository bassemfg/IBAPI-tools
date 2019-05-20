# -*- coding: utf-8 -*-
"""
Created on Mon May 20 12:01:12 2019

@author: bassem yacoube

Code to Download Historical Tick Data for ZB futures contract from IB using the IB API and ib_insync
"""

#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
import os
import pandas as pd

import datetime

try:
	os.chdir(os.path.join(os.getcwd(), '..\..\ib_insync'))
	print(os.getcwd())
except:
	pass
#%%
from ib_insync import *
util.startLoop()

ib = IB()
ib.connect('127.0.0.1', 7498, clientId=15)

#%%
df_ticks = pd.DataFrame(columns=['Timestamp','price','size'])
contracts = [ContFuture('ZB')]
contracts[0].includeExpired=True
#contracts[0].lastTradeDateOrContractMonth='20190318'
ib.qualifyContracts(*contracts)
dt_earliest_available=ib.reqHeadTimeStamp(contracts[0],"TRADES",False,1)
dt_earliest_available=dt_earliest_available.astimezone(tz=datetime.timezone.utc)
#%%
def insert_ticks(df_ticks, ticks):
    data = []
    i=0
    for tick in ticks:
        data.insert(i, {'Timestamp': tick.time, 'price': tick.price, 'size': tick.size})
        i=i+1

    df_ticks=pd.concat([pd.DataFrame(data), df_ticks], ignore_index=True)
    return df_ticks

dt=datetime.datetime.now()
dt=dt.astimezone(tz=datetime.timezone.utc)

while True:
    ticks=ib.reqHistoricalTicks(contracts[0],None,dt,1000,"TRADES",False)

    if dt<=dt_earliest_available:
        break    

    if len(ticks)<2:
        dt=dt-datetime.timedelta(days=1)
    else:
        df_ticks=insert_ticks(df_ticks, ticks)
        dt=ticks[0].time
        print ('Getting tick data for ', dt)

df_ticks.to_csv(r'c:\test\IB-USH19-data.csv')
print(df_ticks)
#%%
ib.disconnect()