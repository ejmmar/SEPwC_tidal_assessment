"""import necessary modules for code to run"""
#import argparse
import datetime
import pandas as pd
import numpy as np
from scipy.stats import linregress
import matplotlib.dates as libdates
import uptide
import pytz



FILENAME= 'data/1947ABE.txt'
FILENAME1 ='data/1946ABE.txt' 


def read_tidal_data(filename):
    """filename has 1947 aberdeen tidal data"""
    #read data with all rows as to name the headers what i want
    #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
    #https://stackoverflow.com/questions/34091877/how-to-add-header-row-to-a-pandas-dataframe
    data = pd.read_csv(filename,sep=r'\s+', skiprows=(0,1,2,3,4,5,6,7,8,9,10),
                       names=['Cycle','Date', 'Time','Sea Level','Residual'])
    data.columns = data.columns.str.replace("ASLVZZ01", "Sea Level")
    #merging date and time columns together and set as index
    #https://www.statology.org/pandas-combine-date-and-time-columns/
    #https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.set_index.html
    data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
    data = data.set_index('DateTime')
    #replace M, N and T with NaN
    data.replace(to_replace=".*M$",value={'Sea Level':np.nan},regex=True,inplace=True)
    data.replace(to_replace=".*N$",value={'Sea Level':np.nan},regex=True,inplace=True)
    data.replace(to_replace=".*T$",value={'Sea Level':np.nan},regex=True,inplace=True)
    #converting from string values to float values
    #https://brainly.com/question/47279360
    data["Sea Level"]=data["Sea Level"].astype(float)
    return data


def extract_single_year_remove_mean(year, data):
    """shows sea level from everyday in the year from 1st jan to 31st dec
    shows what values are not numbers
    removes the mean"""
    year_start = str(year)+"0101"
    year_end = str(year)+"1231"
    year_data = data.loc[year_start:year_end, ['Sea Level']]
    #https://saturncloud.io/blog/what-is-pandas-mean-for-a-certain-column/
    year_data = year_data.apply(pd.to_numeric, errors="raise")
    year_data =(year_data)-(year_data['Sea Level'].mean())
    print (year_data)

    return year_data


def extract_section_remove_mean(start, end, data):
    """takes section of sea level data not necessarily catergorised as years
    removes the mean"""
    #https://pandas.pydata.org/docs/reference/api/pandas.Series.str.extract.html
    section_start = str(start)
    section_end = str(end)
    section_data=data.loc[section_start:section_end, ['Sea Level']]
    #https://saturncloud.io/blog/what-is-pandas-mean-for-a-certain-column/
    #https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html
    section_data = section_data.apply(pd.to_numeric, errors="raise")
    section_data =(section_data)-(section_data['Sea Level'].mean())
    print (section_data)

    return section_data



def join_data(data1, data2):
    """merge filename 1 and 2 to show 1946 and 1947 data in one column"""
    #https://pandas.pydata.org/docs/user_guide/merging.html
    join_data1=pd.concat([data1, data2])
    print(join_data1)
    data=join_data1
    #https://saturncloud.io/blog/how-to-sort-a-pandas-dataframe-by-date/
    data=data.sort_values(by=['DateTime'],ascending=True)

    return data


def sea_level_rise(data):
    """Remove nan from the coloum sea level"""
    #https://www.aporia.com/resources/how-to/drop-rows-pandas-dataframe-column-vamue-nan/
    #https://stackoverflow.com/questions/34843513/python-matplotlib-dates
    #-date2num-converting-numpy-array-to-matplotlib-datetimes
    data = data.dropna(subset=["Sea Level"])
    x_axis= libdates.date2num(data.index)
    y_axis= data["Sea Level"].values
    print(x_axis,y_axis)
    #https://medium.com/@gubrani.sanya2/linear-regression-with-python-ffe0403a4683
    slope, _intercept, _r_value, p_value, _std_err =linregress(x_axis, y_axis)
    return slope, p_value




    #return
def tidal_analysis(data, constituents, start_datetime):
    """extracting consituents from data index """
    #https://github.com/stephankramer/uptide/blob/master/README.md
    data = data.dropna(subset=["Sea Level"]) 
    tide=uptide.Tides(['constituents'])
    tide.set_initial_time(start_datetime)
    time_zone=pytz.timezone("utc")
    seconds= (data.index.astype('int64').to_numpy()
                     /1e9)- datetime.datetime(1946,1,15,0,0,0,tzinfo=time_zone).timestamp()
    #mini course link
    amp,pha = uptide.harmonic_analysis(tide, data["Sea Level"].to_numpy()/1000, seconds)
    print(amp,pha)
    print(uptide.select_constituents(constituents,15*24*60*60))
    #see how many days worth of data we need(14.7653)
    tide = uptide.Tides(constituents)
    print(tide.get_minimum_Rayleigh_period()/86400.)
    return amp, pha


    #return

#def get_longest_contiguous_data(data):


    #return

#if __name__ == '__main__':

    #parser = argparse.ArgumentParser(
                     #prog="UK Tidal analysis",
                     #description="Calculate tidal constiuents and RSL from tide gauge data",
                     #epilog="Copyright 2024, Jon Hill"
                     #)

    #parser.add_argument("directory",
                    #help="the directory containing txt files with data")
    #parser.add_argument('-v', '--verbose',
                    #action='store_true',
                    #default=False,
                    #help="Print progress")

    #args = parser.parse_args()
    #dirname = args.directory
    #verbose = args.verbose
