#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, argparse, os, logging
import pandas as pd
from datetime import datetime, timedelta
from sodapy import Socrata

def createLogger (logName = os.path.splitext(os.path.basename(__file__))[0], logLevel = logging.INFO):
    FORMAT = '[%(asctime)-15s][%(levelname)s]: %(message)s'
    logging.basicConfig(format=FORMAT,level=logLevel)
    logger = logging.getLogger(logName)
    return logger
    
logger = None #createLogger()

def run(argv):
    global logger

    date_format = lambda s: datetime.strptime(s, '%Y-%m-%d')
    yesterday = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)-timedelta(days=1)
    parser = argparse.ArgumentParser(description='Get meteo stations data for Catalonia.')
    parser.add_argument('-o', '--oFolder',  default=os.getcwd(), help='Output folder (default: current folder).')
    parser.add_argument('-f', '--oFile',  help='Output file (default: None). File is updated with new data.')
    parser.add_argument('-d', '--debug', default='INFO', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], help='Logging level.')
   
    #args = parser.parse_args(argv)
    args, unknown = parser.parse_known_args()
    oFolder = args.oFolder
    oFile = args.oFile
    
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
        
    get_meteo_estaciones_cat(oFolder, oFile)
    exit(0)
    
def get_meteo_estaciones_cat(oFile=None): 
    global logger

    # Metadatos estaciones meteorológicas automáticas
    # https://analisi.transparenciacatalunya.cat/es/Medi-Ambient/Metadades-estacions-meteorol-giques-autom-tiques/yqwd-vj5e    
    dataset_identifier = "yqwd-vj5e"
    with Socrata("analisi.transparenciacatalunya.cat", None) as client:
        filename = oFile if oFile else "meteo_stations.json"
        filePath = os.path.join(oFolder, filename)
        logger.info("Write to file: " + filePath)
        with open(filePath, 'w') as f:
            results = client.get(dataset_identifier)
            try:
                f.write(str(results))
            except Exception as inst:
                logger.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
                logger.error(inst)
                pass

if __name__ == '__main__':
    logger = createLogger()
    run(sys.argv[1:])