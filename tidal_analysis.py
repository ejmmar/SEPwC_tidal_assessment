"""import necessary modules for code to run"""
import argparse
import datetime
import glob
import pandas as pd
import numpy as np
from scipy.stats import linregress
import matplotlib.dates as libdates
import uptide

#modules datetime and pytz were imported on test tides to run the tests
#import datetime
#import pytz

#the two data files currently being used
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
    #remove the mean from the whole year
    year_data =(year_data)-(year_data['Sea Level'].mean())
    #view the year data and see the NaN
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
    #remove the mean from the whole section in the testtides
    section_data =(section_data)-(section_data['Sea Level'].mean())
    print (section_data)
    return section_data



def join_data(data1, data2):
    """merge filename 1 and 2 to show 1946 and 1947 data in one column"""
    #https://pandas.pydata.org/docs/user_guide/merging.html
    join_data1=pd.concat([data1, data2])
    print(join_data1)
    data=join_data1
    #join data for 1946 and 1947
    #https://saturncloud.io/blog/how-to-sort-a-pandas-dataframe-by-date/
    data=data.sort_values(by=['DateTime'],ascending=True)
    return data


def sea_level_rise(data):
    """Remove nan from the coloum sea level"""
    #https://www.aporia.com/resources/how-to/drop-rows-pandas-dataframe-column-vamue-nan/
    #https://stackoverflow.com/questions/34843513/python-matplotlib-dates
    #-date2num-converting-numpy-array-to-matplotlib-datetimes
    #dropping nan from sea level
    data = data.dropna(subset=["Sea Level"])
    #https://www.geeksforgeeks.org/matplotlib-dates-dateformatter-class-in-python/
    #named variable libdates for matplotlib
    #x and y variables named with snake_case_named_style
    #time is the x_axis
    x_axis= libdates.date2num(data.index)
    y_axis= data["Sea Level"].values
    #https://medium.com/@gubrani.sanya2/linear-regression-with-python-ffe0403a4683
    slope, _intercept, _r_value, p_value, _std_err =linregress(x_axis, y_axis)
    #return only slope and p_value as it is main ask
    return slope, p_value


def tidal_analysis(data, constituents, start_datetime):
    """extracting constituents from data index """
    #https://jhill1.github.io/SEPwC.github.io/Mini_courses.html#tidal-analysis-in-python
    #https://github.com/stephankramer/uptide/blob/master/README.md
    #make sure nan is not in the merged sea level column
    data = data.dropna(subset=["Sea Level"])
    #constituents is both M2 and S2
    tide=uptide.Tides(constituents)
    tide.set_initial_time(start_datetime)
    #time_zone=pytz.timezone("utc") is written in test so not needed in code
    #call start_datetime function rather than hard code it
    seconds= (data.index.astype('int64').to_numpy()/1e9)- start_datetime.timestamp()
    #https://github.com/stephankramer/uptide
    #elevation data and time in seconds to uptide for the harmonic analysis
    #measured in m
    amp,pha = uptide.harmonic_analysis(tide, data["Sea Level"].to_numpy(), seconds)
    #uptide returns amplitudes and phases in radians
    return amp, pha

def get_longest_contiguous_data(data):
    """"longest sea level data with no NAN"""
    #https://stackoverflow.com/questions/1347791/unicode-error-unicodeescape-
    #codec-cant-decode-bytes-when-writing-windows
    #https://www.reddit.com/r/learnpython/comments/1bogs4y/comment/kwp9w91/
    #https://stackoverflow.com/questions/41494444/pandas-find-longest
    #-stretch-without-nan-values
    data = np.append(np.nan, np.append(data, np.nan))
    # find where null
    nulldata = np.where(np.isnan(data))[0]
    # diff to find length of stretch
    # argmax to find where largest stretch
    length = np.diff(nulldata).argmax()
    # return original positions of boundary nulls
    return nulldata[[length, length + 1]] + np.array([0, -2])

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

    #https://www.youtube.com/watch?v=599ONBvdAfE
    #https://www.geeksforgeeks.org/how-to-read-multiple-data-files-into-pandas/
    txtfiles=[]
    #txtfiles=glob.glob("C:\\Users\\emmaj\\SEPwC_tidal_assessment\\data\\aberdeen\\*.txt")
    txtfiles=glob.glob(str(dirname)+"/*.txt")
    #print(*txtfiles, sep="\n")

    formatting_files=[]
    for file in txtfiles:
        file= read_tidal_data(file)
        formatting_files.append(file)
        #print (formatting_files)
         #print("-------------")

    all_files= join_data(formatting_files[0], formatting_files[1])

    #https://www.programiz.com/python-programming/while-loop
    #https://stackoverflow.com/questions/65902709/pandas-increment-counter-on-condition
    #loop for length of all text files 
    Counter = 0 
    while Counter<(len(txtfiles)):
        all_files= join_data(all_files, formatting_files[Counter])
        Counter = Counter + 1

    #https://www.geeksforgeeks.org/ways-to-remove-ith-character-from-string-in-python/
    #create string to remove unnecessary characters
    M2=str(tidal_analysis(all_files, ['M2'], (datetime.datetime(2000,1,1 ,0, 0, 0)))) 
    print(M2[8:13]) 

    S2=str(tidal_analysis(all_files, ['S2'], (datetime.datetime(2000,1,1, 0, 0, 0))))
    print(S2[8:13])       

    print(sea_level_rise(all_files)[1])

    #boundaries of only contiguous no NAN sea level
    sealevelnonan= all_files['Sea Level']
    print (get_longest_contiguous_data(sealevelnonan))