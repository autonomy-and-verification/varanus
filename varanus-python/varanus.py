import time
from monitor import *
import logging
import argparse
import os
import sys
import csv
from os.path import exists

################
###CONSTANTS###
VERSION_NUM = '0.88.1'

IP = '127.0.0.1'
PORT = 5088
###############

### Arguments###
argParser = argparse.ArgumentParser()
argParser.add_argument("model", help="The location of the model used as the oracle.", default = "model/mascot-safety-system.csp")
argParser.add_argument("map", help="The location of the event map", default = "event_map.json")
argParser.add_argument("type", help="The type of check to be performed", choices=['offline', 'online'])
argParser.add_argument("-n", "--name", help="The name of the check and therefore name of the log file")
argParser.add_argument("--log_path", help="The path of the log dir")
argParser.add_argument("-t", "--trace_file", help="The location of the trace file. Only used if type='offline'")
argParser.add_argument("-s", "--speed", help="Run 10 timed run and produce the times and mean.).", type=bool, default = False)

args = argParser.parse_args()

MODEL = args.model
MAP = args.map
TYPE = args.type
SPEED_CHECK = args.speed
TRACE_FILE = args.trace_file
if args.name:
    CHECK_NAME = args.name
else:
    CHECK_NAME = "scenario x"
if args.log_path:
    LOG_PATH = args.log_path + "/"
else:
    LOG_PATH = "log/"
#TODO check and warn for incompatible params

################
#set to the name of the scenario
logFileName = args.name
log_level = logging.INFO

if not os.path.exists("log"):
    os.mkdir("log")

varanus_logger = logging.getLogger("varanus")
varanus_logger.setLevel(log_level)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


fileHandler = logging.FileHandler(LOG_PATH + "varanus-"+ TYPE +"-"+logFileName+"-"+time.strftime("%Y_%m_%d-%H:%M:%S")+ ".log")

fileHandler.setFormatter(formatter)

varanus_logger.addHandler(fileHandler)

def run(check_type):

        if check_type == "offline":
            t0 = time.time()
            mon = Monitor(MODEL, MAP)
            mon._run_offline_traces_single(TRACE_FILE)
        elif check_type == "online":
            t0 = time.time()
            mon = Monitor(MODEL, MAP)
            mon.run_online_traces_accumulate(IP, PORT, timeRun=False)

        #mon.run_online('127.0.0.1', 5044)
        #mon.run_online_websocket('127.0.0.1', 8080)
        mon.close()
        t1 = time.time()

        total = t1-t0

        return total

def log_speed(name, time):

    file_name = "log/speed-check-"+name+".csv"

    #If the file doesn't exist, open and close it -_-
    if not exists(file_name):
        output_file = open(file_name , "a")
        output_file.close()

    #Read the file to the end to get how many runs it has in it
    output_file = open(file_name , "r")
    csv_read = csv.reader(output_file, delimiter=',', quotechar='"')
    run_num = 0
    for run in csv_read:
        run_num += 1
    output_file.close()

    #Write the number of runs +1 into the file, with the time.
    output_file = open(file_name, "a")
    csv_write = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    run_num += 1
    csv_write.writerow([ "Run" + str(run_num) , time ])
    output_file.close()

print("+++++++++++++++++++++++")
print("+++++++ VARANUS +++++++")
print("++++ version " + str(VERSION_NUM) + " +++")
print("++++ Matt Luckcuck ++++")
print("+++++++++++++++++++++++")
print("")



varanus_logger.debug("Varanus Running v" + str(VERSION_NUM))

varanus_logger.info("+++ Testing " + logFileName + " +++")



    #mon.run_offline_rosmon("../rosmon-test/rosmon-mascot-pass.json")
    #mon._run_offline_traces("trace.json")

##NOW IN RUN
#    if TYPE == "offline":
#        t0 = time.time()
#        mon = Monitor(MODEL, MAP)
#        mon._run_offline_traces_single(TRACE_FILE)
#    elif TYPE == "online":
#        t0 = time.time()
#        mon = Monitor(MODEL, MAP)
#        mon.run_online_traces_accumulate(IP, PORT, timeRun=False)

    #mon.run_online('127.0.0.1', 5044)
    #mon.run_online_websocket('127.0.0.1', 8080)
#    mon.close()
#    t1 = time.time()

total = run(TYPE)

varanus_logger.info("+++ Time: "+ str(total) +"s +++")

varanus_logger.debug("Varanus Finished")

if SPEED_CHECK == True:

    log_speed(CHECK_NAME, total)
