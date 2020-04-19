#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, argparse, inspect, os, logging
import zipfile
import pandas as pd
import numpy as np
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
    parser = argparse.ArgumentParser(description='Get meteo data for Catalonia.')
    parser.add_argument('-s', '--start', type=date_format, default=yesterday, help='Start time (format: yyyy-mm-dd) (default: yesterday).')
    parser.add_argument('-e', '--end', type=date_format, default=yesterday, help='End time (format: yyyy-mm-dd) (default: yesterday).')
    parser.add_argument('-c', '--cities', nargs='*', default=['Barcelona'], help='Filter per cities (default: Barcelona).')
    parser.add_argument('-v', '--variables', nargs='*', help='Filter per observed variables.')
    parser.add_argument('-o', '--oFolder', default=os.getcwd(), help='Output folder (default: current folder).')
    parser.add_argument('-f', '--oFile',  help='Output file (default: None). File is updated with new data.')
    parser.add_argument('-z', '--zip', action='store_true', help='Generate ZIP file')
    parser.add_argument('-d', '--debug', default='INFO', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], help='Logging level.')
   
    args, unknown = parser.parse_known_args()
    start = args.start
    end = args.end.replace(hour=23)
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
        
    scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    
    # if filter per cities is selected -> check correct cities and get station codes
    stationCodes=[]
    if cities:
        logger.info("Check parameter: cities")
        
        # Read meteo stations metadata file
        meteoStationsPath=os.path.join(scriptPath, 'meta\meteo_stations.json')
        if not os.path.exists(meteoStationsPath):
            meteoStationsPath='https://analisi.transparenciacatalunya.cat/resource/yqwd-vj5e.json'
        logger.info('Read meteo stations metadata file: ' + meteoStationsPath)
        meteoStations=pd.read_json(meteoStationsPath, orient='records', encoding='utf-8')
        logger.debug('Content meteo stations metadata:')
        logger.debug(meteoStations)
        
        # Check correct selected cities
        correctCities= [value for value in cities if value in meteoStations['nom_municipi'].values]        
        logger.info("Correct cities:")
        logger.info(correctCities)
        
        # Get station codes for selected correct cities
        stationCodes=np.reshape(meteoStations.loc[meteoStations["nom_municipi"].isin(correctCities), ['codi_estacio']].values,-1).tolist()
        logger.info("Selected codes of stations:")
        logger.info(stationCodes)
    
    # if filter per variables is selected -> check correct variables and get variable codes
    variableCodes=[]
    if variables:
        logger.info("Check parameter: variables")
        
        # Read meteo variables metadata file
        meteoVariablesPath=os.path.join(scriptPath, 'meta\meteo_variables.json')
        if not os.path.exists(meteoVariablesPath):
            meteoVariablesPath='https://analisi.transparenciacatalunya.cat/resource/4fb2-n3yi.json'
        logger.info('Read meteo variables metadata file: ' + meteoVariablesPath)
        meteoVariables=pd.read_json(meteoVariablesPath, orient='records', encoding='utf-8')
        logger.debug('Content meteo variables metadata:')
        logger.debug(meteoVariables)  
        
        # Check correct selected variables
        correctVariables= [value for value in variables if value in meteoVariables['acronim'].values]
        logger.info("Correct variables:")
        logger.info(correctVariables)
        
        # Get variable codes for selected correct variables
        variableCodes=np.reshape(meteoVariables.loc[meteoVariables["acronim"].isin(correctVariables), ['codi_variable']].values,-1).tolist()
        logger.info("Selected codes of variables:")
        logger.info(variableCodes)
    
    # Get meteo data for filter
    count = get_meteo_cat(start, end, stationCodes, variableCodes, oFolder, oFile, genZip)
    logger.info(str(count))
    exit(0)
    
"""
    Function: get_meteo_cat
    
    Get meteo data from the open data service of Catalonya 
"""
def get_meteo_cat(start, end, stationCodes=[], variableCodes=[], oFolder=None, oFile=None, genZip=False): 
    global logger
    
    stationCodes = [None] if stationCodes is None else [None] if len(stationCodes) == 0 else stationCodes
    variableCodes = [None] if variableCodes is None else [None] if len(variableCodes) == 0 else variableCodes
     
    count = 0
    SEP=';'
    # Dades meteorològiques de la XEMA
    # https://analisi.transparenciacatalunya.cat/es/Medi-Ambient/Dades-meteorol-giques-de-la-XEMA/nzvn-apee
    dataset_identifier = "nzvn-apee"
    with Socrata("analisi.transparenciacatalunya.cat", None) as client:

        filename=''
        prevfilename=''
        
        # Loop to get meteo data per each hour
        time_range = pd.date_range(start, end, freq='H') # Data is hourly recorded
        for time in time_range:
        
            # Build output filename
            filename = oFile if oFile else str(time.strftime("meteo_%Y_%m.csv"))
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
                # Get meteo data at time and per every station and variable codes
                for stationCode in stationCodes:
                    logger.debug("Get data for station code: " + str(stationCode))
                    for variableCode in variableCodes:
                        logger.debug("Get data for variable code: " + str(variableCode))
                        
                        tries = 0
                        while tries < 5:
                            try:
                                # Send query to meteo data service
                                results = client.get(dataset_identifier, limit=20000, content_type="csv", 
                                                data_lectura=str(time.strftime("%Y-%m-%dT%H:%M:%S.000")), 
                                                CODI_ESTACIO=stationCode, 
                                                CODI_VARIABLE=variableCode)
                                break
                            except:
                                tries+=1
                            
                        try:
                            # Write meteo data to output file
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