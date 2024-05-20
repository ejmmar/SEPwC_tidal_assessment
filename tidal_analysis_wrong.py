#!/usr/bin/env python3

# import the modules you need here
import argparse
import pandas as pd
import numpy as np

FILENAME= 'data/1947ABE.txt'
FILENAME1 ='data/1946ABE.txt'


def read_tidal_data(filename):
    #read data with all rows as to name the headers what i want
    #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
    #https://stackoverflow.com/questions/34091877/how-to-add-header-row-to-a-pandas-dataframe
     = pd.read_csv(FILENAME,sep=r'\s+', skiprows=(0,1,2,3,4,5,6,7,8,9,10),
                       names=['Cycle','Date', 'Time','Sea Level','Residual'])
    DATA.columns = DATA.columns.str.replace("ASLVZZ01", "Sea Level")
    #merging date and time columns together and set as index
    #https://www.statology.org/pandas-combine-date-and-time-columns/
    #https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.set_index.html
    DATA['DateTime'] = pd.to_datetime(DATA['Date'] + ' ' + DATA['Time'])
    DATA = DATA.set_index('DateTime')
    #replace M, N and T with NaN
    DATA.replace(to_replace=".*M$",value={'Sea Level':np.nan},regex=True,inplace=True)
    DATA.replace(to_replace=".*N$",value={'Sea Level':np.nan},regex=True,inplace=True)
    DATA.replace(to_replace=".*T$",value={'Sea Level':np.nan},regex=True,inplace=True)

    return DATA

read_tidal_data(FILENAME)


def extract_single_year_remove_mean(year, data):
    year_start = str(year)+"0101"
    year_end = str(year)+"1231"
    year_data = data.loc[year_start:year_end, ['Sea Level']]
    #https://saturncloud.io/blog/what-is-pandas-mean-for-a-certain-column/
    year_data = year_data.apply(pd.to_numeric, errors="raise")
    year_data =(year_data)-(year_data['Sea Level'].mean())
    print (year_data)

    return year_data


def extract_section_remove_mean(start, end, data):
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
    #https://pandas.pydata.org/docs/user_guide/merging.html
    join_data=pd.concat([data1, data2])
    print(join_data)
    data=join_data
    data=data.sort_values(by=['DateTime'],ascending=True)

    return data



def sea_level_rise(data):


    return

def tidal_analysis(data, constituents, start_datetime):


    return

def get_longest_contiguous_data(data):


    return

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                     prog="UK Tidal analysis",
                     description="Calculate tidal constiuents and RSL from tide gauge data",
                     epilog="Copyright 2024, Jon Hill"
                     )

    parser.add_argument("directory",
                    help="the directory containing txt files with data")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args()
    dirname = args.directory
    verbose = args.verbose
