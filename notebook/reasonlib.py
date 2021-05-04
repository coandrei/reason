"""
Created on Thu Apr 15 13:38:24 2019

Functions to be used in connection with the GRC-GRANT-04 project
 
Copyright: Octavian Andrei (FGI/NLS), 2019
"""

import numpy as np
import pandas as pd
import os


def readRnxNavFile(filepath: str):
    """Read one navigation file and outputs a list of navigation messages from the file
    One navigation message is a list of elements that are associated with the message.
    
    Arguments:
        filepath : str
            path to the rinex v3.X navigation file
    
    Returns:
        header   : list of strings, 
        navdata  : list of list of values
    
    Note:
        [1] Rinex v3.04 guidelines
    """
    
    # initiate the lists to hold the navigation header and data
    hdrdata = []
    navdata = []
    
    # parse a navigation record line (it works for orbit lines 1-7)
    def parse_navline(line: str):
        return [line[19*i:19*(i+1)].strip().upper().replace('D','E') for i in range(4)]
    
    # navigation header labels
    header_labels = (
        'RINEX VERSION / TYPE',
        'PGM / RUN BY / DATE',
        'COMMENT',
        'IONOSPHERIC CORR',
        'TIME SYSTEM CORR',
        'LEAP SECONDS',
        'END OF HEADER',
    )
    
    # read the input file
    ext = os.path.splitext(filepath)[1].lower();
    if ext == '.gz': import gzip; f = gzip.open(filepath, 'rt');
    else: f = open(filepath, 'rt'); 

    for line in iter(f.readline, ""):
        # header lines
        if any(label in line for label in header_labels):
            #print(line.strip('\n'));
            hdrdata.append(line.strip('\n'))

        # data lines
        else:

            # initialize container for one navigation message
            data = []

            # this is the 1st record line of the navigation message (as in [1])
            if line[0] in ('E', 'G', 'Q', 'C', 'I'): 
                nlines = 7;
            elif line[0] in ('R', 'S'):
                nlines = 3;

            # catch the satid and time of clock
            prn = line[:3].replace(' ','0') #string
            toc = [int(item) for item in line[4:23].split()] #list of int

            # the remaining of the 1st record line
            data.append(
                [
                    line[23:][19*i:19*(i+1)].strip().upper().replace('D','E') 
                    for i in range(3)
                ]
            )

            # next N record lines (incomplete message will break the code)
            # i.e. broadcast orbit 1-7 as in [1]
            data += [
                parse_navline(line[4:]) 
                for line 
                in [next(f).strip('\n') for i in range(nlines)]
            ]

            # convert to floats or NaN
            from numpy import NaN
            data = [prn] + toc + [
                float(item) if item else NaN 
                for line in data 
                for item in line
            ]

            navdata.append(data)
    
    # close file
    f.close();
    
    return hdrdata, navdata
