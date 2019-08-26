#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Analysis of German Renewables - Time Series 


# In[75]:


#This time Series is in a 60 minute frequency
#Countries are rapidly expanding their country toals of elecricity consumption
#The Data set can be found in the Github Repository or here at - https://data.open-power-system-data.org/time_series/2019-06-05
#The readme for the data is here: https://data.open-power-system-data.org/time_series/2019-06-05/README.md

#Import needed modules
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
plt.rcParams["figure.figsize"] = (10,5)
import matplotlib.dates as mdates
import numpy as np

#I've filtered the data on the download website to just Germany and the data will be from 2015-01-01 to 2019-05-01
#https://data.open-power-system-data.org/time_series/2019-06-05
opsd_60min = pd.read_csv(r'C:\Users\agilarde\Downloads\time_series_60min_singleindex_filtered.csv',index_col=0,parse_dates=True)


# In[76]:


opsd_60min.shape


# In[77]:


#So we have 500k rows and 77 columns
#Let's see the head
opsd_60min.head(5)


# In[78]:


opsd_60min.tail(5)


# In[79]:


#A breakdown of the variables can be found in the Readme
#However, I'm interested in Germany's Solar + Wind Generation 
#The variables we are interested in are as follows:
#* utc_timestamp
#    - Type: datetime
#    - Format: fmt:%Y-%m-%dT%H%M%SZ
#    - Description: Start of timeperiod in Coordinated Universal Time

#* DE_wind_generation_actual
#    - Type: number
#    - Description: Actual wind generation in Germany in MW

#* DE_solar_generation_actual
#    - Type: number
#    - Description: Actual solar generation in Germany in MW

#* DE_load_actual_entsoe_transparency
#    - Type: number
#    - Description: Total load in Germany in MW as published on ENTSO-E Transparency Platform

#Sum the columns for later use
opsd_60min['german_renewables'] = opsd_60min["DE_wind_onshore_generation_actual"] + opsd_60min['DE_solar_generation_actual'] 
opsd_60min['german_ratio'] = opsd_60min["german_renewables"]/opsd_60min["DE_load_actual_entsoe_transparency"]
#Define the data frame as the few variables we'd like to analyze
df=opsd_60min[["DE_wind_onshore_generation_actual","DE_solar_generation_actual","german_renewables","DE_load_actual_entsoe_transparency","german_ratio"]]
df.columns = ["german_wind","german_solar","german_renewables","consumption","ratio"]


# In[80]:


## Visualize our Data


# In[81]:


ax = df.loc['2016-09':'2017-02', 'consumption'].plot(linestyle='-')
ax.set_ylabel('Daily Consumption (GWh)');

#This is interesting because it would seem that consumption isn't necessarilly affacted in the winter, however it drops
#in Jan.


# In[82]:


cols_plot = ['consumption', 'german_solar', 'german_wind']
axes = df[cols_plot].plot(marker='.', alpha=0.5, linestyle='None', figsize=(20, 10), subplots=True)
for ax in axes:
    ax.set_ylabel('Daily Totals (GWh)')


# In[83]:


#Let's see the vertical gride as tick lables on each monday so we can tell when the weeks change
#Let's also zoom in on that drop in december to Jan consumption

fig, ax = plt.subplots()
ax.plot(df.loc['2016-12':'2017-01', 'consumption'], linestyle='-')
ax.set_ylabel('Daily Consumption (GWh)')
ax.set_title('Sep-Feb 2016-2017 Electricity Consumption')
# axis ticks to weekly interval, on Mondays
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MONDAY))
# tick labels as 3-letter month name and day number
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'));


# In[84]:


## Means & Resampling


# In[85]:


#Now I want to re-sample and plot a few different ways to be able to better understand the statistics involved
#plus this allows our time series to have significantly less data points to handle than the hourly time series

# Specify the data columns we want to include
data_columns = ['consumption', 'german_wind', 'german_solar', 'german_renewables','ratio']
# Resample to weekly frequency, aggregating with mean
df_daily_mean = df[data_columns].resample('D').mean()
df_weekly_mean = df[data_columns].resample('W').mean()
df_month_mean = df[data_columns].resample('M').mean()
df_yearly_mean = df[data_columns].resample('Y').mean()
df_monthly = df[data_columns].resample('M').sum()
df_daily = df[data_columns].resample('D').sum()
df_yearly = df[data_columns].resample('Y').sum()
df_weekly = df[data_columns].resample('W').sum()


# In[86]:


#Quick check on how many rows each have now that I've resampled
print(df_daily_mean.shape[0])
print(df_weekly_mean.shape[0])
print(df_month_mean.shape[0])
print(df_yearly_mean.shape[0])
print(df_monthly.shape[0])


# In[87]:


#Let's plot
start, end = '2016-09', '2017-06'
# Plot daily and weekly resampled time series together
fig, ax = plt.subplots()
ax.plot(df_daily_mean.loc[start:end, 'german_solar'], linestyle='-', linewidth=1, label='Daily')
ax.plot(df_weekly_mean.loc[start:end, 'german_solar'],
marker='o', markersize=1, linestyle='-', label='Weekly Mean Resample')
ax.set_ylabel('Solar Production (GWh)')
ax.legend();


# In[88]:


#Rolling mean
df_7d = df_daily[data_columns].rolling(7, center=True).mean()

#Plot
start, end = '2016-09', '2017-06'
# Plot daily, weekly resampled, and 7-day rolling mean time series together
fig, ax = plt.subplots()
ax.plot(df_daily.loc[start:end, 'german_solar'],
marker='.', linestyle='-', linewidth=0.5, label='Daily')

ax.plot(df_7d.loc[start:end, 'german_solar'],
marker='.', linestyle='-', label='7-d Rolling Mean', color ='green')
ax.set_ylabel('Solar Production (GWh)')
ax.legend();


# In[89]:


## Trends


# In[90]:


#let's calculate a 365d rolling mean as well
df_365d = df_daily[data_columns].rolling(window=365, center=True, min_periods=360).mean()


# In[91]:


# Plot daily, 7-day rolling mean, and 365-day rolling mean time series
fig, ax = plt.subplots()
ax.plot(df_daily['consumption'], marker='.', markersize=2, color='0.6',
linestyle='None', label='Daily')
ax.plot(df_7d['consumption'], linewidth=2, label='7-d Rolling Mean')
ax.plot(df_365d['consumption'], color='0.2', linewidth=3,
label='Trend (365-d Rolling Mean)')
# Set x-ticks to yearly interval and add legend and labels
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.legend()
ax.set_xlabel('Year')
ax.set_ylabel('Consumption (GWh)')
ax.set_title('Trends in Electricity Consumption');


# In[92]:


# Plot 365-day rolling mean time series of wind and solar power
fig, ax = plt.subplots()
for nm in ['german_wind', 'german_solar', 'german_renewables']:
    ax.plot(df_365d[nm], label=nm)
# Set x-ticks to yearly interval, adjust y-axis limits, add legend and labels
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.set_ylim(0)
ax.legend()
ax.set_ylabel('Production (GWh)')
ax.set_title('Trends in Electricity Production (365-d Rolling Means)');


# In[93]:


## Future Ideas - Forecasting using different models


# In[94]:


from statsmodels.tsa.stattools import acf, pacf


# In[95]:


df_predict=df_weekly[["german_solar","german_wind"]]
df_predict.columns = ["wind","solar"]


# In[110]:


plt.hist(df_predict['solar'], alpha=0.5, label='Solar')
plt.hist(df_predict['wind'], alpha=0.5, label='Wind')


# In[112]:


dflog['solar'] = np.log10(df_predict['solar'])
dflog['wind'] = np.log10(df_predict['wind'])

plt.hist(dflog['solar'], alpha=0.5, label='Solar')
plt.hist(dflog['wind'], alpha=0.5, label='Wind')


# In[ ]:




