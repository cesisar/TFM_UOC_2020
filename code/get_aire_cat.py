#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, argparse, os, logging
import zipfile
import pandas as pd
import codecs
from datetime import datetime, timedelta
from dateutil.parser import *
from sodapy import Socrata
    
def createLogger (logName = os.path.splitext(os.path.basename(__file__))[0], logLevel = logging.INFO):
    FORMAT = '[%(asctime)-15s][%(levelname)s]: %(message)s'
    logging.basicConfig(format=FORMAT,level=logLevel)
    logger = logging.getLogger(logName)
    return logger
    
logger = None #createLogger()

def run(argv):
    global logger

    #date_format = lambda s: datetime.strptime(s, '%Y-%m-%d')
    date_format = lambda s: parse(s)
    yesterday = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)-timedelta(days=1)
    parser = argparse.ArgumentParser(description='Get air quality data for Catalonia.')
    parser.add_argument('-s', '--start', type=date_format, default=yesterday, help='Start time (format: yyyy-mm-dd) (default: yesterday).')
    parser.add_argument('-e', '--end', type=date_format, default=yesterday.replace(hour=23), help='End time (format: yyyy-mm-dd) (default: yesterday).')
    parser.add_argument('-c', '--cities', nargs='*', default=['Barcelona'], help='Filter per cities (default: Barcelona).')
    parser.add_argument('-v', '--variables', nargs='*', help='Filter per observed variables.')
    parser.add_argument('-o', '--oFolder',  default=os.getcwd(), help='Output folder (default: current folder).')
    parser.add_argument('-f', '--oFile',  help='Output file (default: None). File is updated with new data.')
    parser.add_argument('-z', '--zip', action='store_true', help='Generate ZIP file')
    parser.add_argument('-d', '--debug', default='INFO', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], help='Logging level.')
   
    args, unknown = parser.parse_known_args()
    start = args.start
    end = args.end
    cities = args.cities
    variables = args.variables
    oFolder = args.oFolder
    oFile = args.oFile
    genZip = args.zip
    
    lutLogLevel = { 
        "CRITICAL" : logging.CRITICAL, 
        "ERROR" : logging.ERROR, 
        "WARNING" : logging.WARNING, 
        "INFO" : logging.INFO, 
        "DEBUG" : logging.DEBUG, 
        "NOTSET" : logging.NOTSET }
    logLevel = lutLogLevel[args.debug]
    logger = createLogger()
    logger.setLevel(logLevel)
    
    if start > end:
        logger.error("Error input times.")
        exit(1)
    
    # Get air quality data for filter
    count = get_aire_cat(start, end, cities, variables, oFolder, oFile, genZip)
    logger.info(str(count))
    exit(0)

"""
    Function: get_meteo_cat
    
    Get air quality data from the open data service of Catalonya 
"""
def get_aire_cat(start, end, cities=[], variables=[], oFolder=None, oFile=None, genZip=False): 
    global logger
 
    cities = [None] if cities is None else [None] if len(cities) == 0 else cities
    variables = [None] if variables is None else [None] if len(variables) == 0 else variables
    
    count = 0
    SEP=';'
    # Dades d’immissió dels punts de mesurament de la Xarxa de Vigilància i Previsió de la Contaminació Atmosfèrica
    # https://analisi.transparenciacatalunya.cat/es/Medi-Ambient/Dades-d-immissi-dels-punts-de-mesurament-de-la-Xar/uy6k-2s8r
    dataset_identifier = "uy6k-2s8r"
    with Socrata("analisi.transparenciacatalunya.cat", None) as client:
    
        filename=''
        prevfilename=''
        
        # Loop to get air quality data per each hour
        time_range = pd.date_range(start, end, freq='D') # Data is daily recorded
        for time in time_range:
        
            # Build output filename
            filename = oFile if oFile else str(time.strftime("aire_%Y_%m.csv"))
            filePath = os.path.join(oFolder, filename)
            
            # Check if there is change of output file
            if filename != prevfilename: 
                logger.info("Write to file: " + filePath)
                
                # Zip output file, if so
                if (prevfilename != '') & genZip:
                    prevfilePath = os.path.join(oFolder, prevfilename)
                    zf = zipfile.ZipFile(prevfilePath.replace('.csv','.zip'), 'w', zipfile.ZIP_DEFLATED, allowZip64 = True)
                    zf.write(prevfilePath, prevfilename)
                    zf.close()
                
            # Open output file
            with codecs.open(filePath, 'a', encoding='utf8') as f:
                logger.info("Time: " + str(time.strftime("%Y-%m-%dT%H:%M:%S.000")))
                # Get air quality data at time and per every selected city and variable
                for city in cities:
                    logger.debug("Get data for city: " + str(city))
                    for variable in variables:
                        logger.debug("Get data for variable: " + str(variable))
                        tries = 0
                        while tries < 5:
                            try:
                                # Send query to air quality data service
                                results = client.get(dataset_identifier, limit=20000, content_type="csv", 
                                                ANY=time.year, MES=time.month, DIA=time.day, 
                                                MUNICIPI=city, 
                                                CONTAMINANT=variable)
                                break
                            except:
                                tries+=1
                                
                        try:
                            # Write air quality data to output file
                            del results[0] # remove header
                            for data in results:
                                logger.debug(SEP.join(data))
                                f.write(SEP.join(data) + "\n")
                                count+=1
                        except Exception as inst:
                            logger.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
                            logger.error(inst)
                            pass
                    
            prevfilename = filename
            
        # Last generated file must be zipped, if so
        if (filename != '') & genZip:
            filePath = os.path.join(oFolder, filename)
            zf = zipfile.ZipFile(filePath.replace('.csv','.zip'), 'w', zipfile.ZIP_DEFLATED, allowZip64 = True)
            zf.write(filePath, filename)
            zf.close()
                
    return count

        
if __name__ == '__main__':
    logger = createLogger()
    run(sys.argv[1:])