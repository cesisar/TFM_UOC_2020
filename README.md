# Pollution forecast for the city of barcelona using supervised models

This repository includes everything needed to obtain the results from the following Master's thesis (TFM - Trabajo Fin de Máster):

    Title: Predicción de índices de contaminación del aire mediante modelos supervisados para la ciudad de Barcelona
    Author: César Fernández Domínguez
    Tutor:  Sergio Trilles Oliver
            Albert Solé Ribalta
    
    Data Science Master - Universitat Oberta de Cataluyna (UOC)
    Data Mining & Machine learning

This work was carried out during the first quarter of the year 2020. And it was presented in the month of June 2020. All the data used in this work was downloaded from open sources. 

# Folder structure (source code and data)

All the source code and data needed to get the results for this TFM have been organized in the following folder structure:

    code/ --------------------------- source code
    data/ --------------------------- folder to contain TFM data
    data/aire ----------------------- air pollution data
    data/meteo ---------------------- weather data
    data/meteo/meta ----------------- metadata for meteo data (related to meteo variables and stations)
    data/trafico -------------------- trafic data
    data/trafico/meta --------------- metadata for trafic data (road sections)
  
Additionally, some partial results have been recorded on the following folders:

    data/
    data/tuning ------------------- contains results for hyperparameter adjustment
    data/tuning/fs ---------------- results using forward selection method for select independant variables
    data/tuning/pca0 -------------- results using most relevant varibles from first component of PCA analysis 
                                    for select independant variables
    data/tuning/pcas -------------- results using first most relevant variables from each component of PCA 
                                    analysis for select independant variables
    data/tuning/total ------------- results using all the variables as independant variables

# Code description and execution

This project has been conducted taking account the methodology for data science projects, CRISP-DM (Cross Industry Standard Process for Data Mining). This methodology follows the life cycle of a common data science project. It consist on the following phases:

- Phase I. Business Understanding.
- Phase II. Data Understanding.
- Phase III. Data Preparation.
- Phase IV. Modeling.
- Phase V. Evaluation.
- Phase VI. Deployment.

Every one of these phases are briefly explained in the TFM's memory. 

Following, a brief description of the source code is included.

## Data download

First, a serie of python scripts are provided to download air pollution and weather data from the Open Sources (traffic data is directly downloaded from the webpage of the Ajuntament de Barcelona's open data service) 

### Download air pollution data 

This script allows to download air pollution data for any Catalonian city from a given range. For this TFM, data have been downloaded from Jannuary 2010 to May 2020 (downloaded data can be found in the data folder: data/air).

The syntax for the *get_aire_cat.py* script is:

    usage: get_aire_cat.py [-h] [-s START] [-e END] [-c [CITIES [CITIES ...]]]
                           [-v [VARIABLES [VARIABLES ...]]] [-o OFOLDER]
                           [-f OFILE] [-z]
                           [-d {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}]

    Get air quality data for Catalonia.

    optional arguments:
      -h, --help            show this help message and exit
      -s START, --start START
                            Start time (format: yyyy-mm-dd) (default: yesterday).
      -e END, --end END     End time (format: yyyy-mm-dd) (default: yesterday).
      -c [CITIES [CITIES ...]], --cities [CITIES [CITIES ...]]
                            Filter per cities (default: Barcelona).
      -v [VARIABLES [VARIABLES ...]], --variables [VARIABLES [VARIABLES ...]]
                            Filter per observed variables.
      -o OFOLDER, --oFolder OFOLDER
                            Output folder (default: current folder).
      -f OFILE, --oFile OFILE
                            Output file (default: None). File is updated with new
                            data.
      -z, --zip             Generate ZIP file
      -d {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}, --debug {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
                            Logging level.

### Download weather data

Three python scripts have been written to download the needed data:

- get_meteo_cat.py
- get_meteo_estaciones_cat.py
- get_meteo_variables_cat.py

First script, *get_meteo_cat.py*, is used to download weather data from Barcelona city. Data have been downloaded for the period from Jannuary 2010 to May 2020. The downloaded data is available in the folder: data/meteo

The syntax for the *get_meteo_cat.py* script is:

    usage: get_meteo_cat.py [-h] [-s START] [-e END] [-c [CITIES [CITIES ...]]]
                            [-v [VARIABLES [VARIABLES ...]]] [-o OFOLDER]
                            [-f OFILE] [-z]
                            [-d {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}]

    Get meteo data for Catalonia.

    optional arguments:
      -h, --help            show this help message and exit
      -s START, --start START
                            Start time (format: yyyy-mm-dd) (default: yesterday).
      -e END, --end END     End time (format: yyyy-mm-dd) (default: yesterday).
      -c [CITIES [CITIES ...]], --cities [CITIES [CITIES ...]]
                            Filter per cities (default: Barcelona).
      -v [VARIABLES [VARIABLES ...]], --variables [VARIABLES [VARIABLES ...]]
                            Filter per observed variables.
      -o OFOLDER, --oFolder OFOLDER
                            Output folder (default: current folder).
      -f OFILE, --oFile OFILE
                            Output file (default: None). File is updated with new
                            data.
      -z, --zip             Generate ZIP file
      -d {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}, --debug {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
                            Logging level.

The other two scripts are used to download weather stations metadata, *get_meteo_estaciones_cat.py*, and weather variables metadata, *get_meteo_variables_cat.py*

## Data exploration and preparation

Phases II and III of the CRISP-DM methodology are performed in the following three jupyther notebooks:

- 1_analisis_data_aire.ipynb ----------- air pollution data exploration and preparation
- 1_analisis_data_meteo.ipynb ---------- weather data exploration and preparation
- 1_analisis_data_trafico.ipynb -------- traffic data exploration and preparation

In these scripts, downloaded data is loaded, a brief exploration of the data is performed and some data transformation are done in order to prepare all the data as time series to our machine learning models.

## Hyperparameters adjustment

A hyperparameter adjustment has been made for the prediction models proposed in this TFM. All the process carried out is included in the next two jupyther notebooks:

- 2_ajuste_hiperparametros.ipynb ------------- hyperparameter adjustement and variables selection
- 3_ajuste_hiperparametros_eval.ipynb -------- evaluation of the previous results

## Models evaluation

Finally, a last jupyther notebooks is included containing models training and evaluation. A comparition is performed to the results of the different prediction models for several predicted pollulants in each of the selection air stations. The jupyther notebook containing this part is:

- 4_evaluacion_modelos.ipynb ----------------- models training and evaluation
