# coding=utf-8
import time
from monitor import *
from time_store import Time_Store
import logging
import argparse
import os
import sys
import csv
from os.path import exists
import yaml

################
###CONSTANTS###
VERSION_NUM = '0.9.2'

IP = '127.0.0.1'
PORT = 5088
###############

### Arguments###
argParser = argparse.ArgumentParser()
argParser.add_argument("type", help="The type of check to be performed",
                       choices=['offline', 'online', 'sm-test', 'offline-test', 'stress_test'])
argParser.add_argument("config", help="The location of the config file")
argParser.add_argument("--model", help="The location of the model used as the oracle.",
                       default="model/mascot-safety-system.csp")
argParser.add_argument("--map", help="The location of the event map", default="event_map.json")
argParser.add_argument("-n", "--name", help="The name of the check and therefore name of the log file")
argParser.add_argument("--log_path", help="The path of the log dir")
argParser.add_argument("-t", "--trace_file", help="The location of the trace file. Only used if type='offline'")
argParser.add_argument("-s", "--speed", help="Run 10 timed run and produce the times and mean.", type=bool,
                       default=False)

args = argParser.parse_args()

# TODO check and warn for unopenable filepaths
# TODO Tidy this mess up
# TODO I think the way to handle the file paths is to take them as relative to where the file is and convert to absolute. Maybe?
CONFIG_FILE = args.config
config_path = args.config
config_path_prefix = os.path.dirname(config_path) +"/"
varanus_logger.debug("path prefix = " + config_path_prefix)
with open(config_path, 'r') as data:
    config = yaml.safe_load(data)

    if 'alphabet' in config:
        EXPLICIT_ALPHABET = False
        ALPHABET = set(config['alphabet'])
    if 'main_process' in config:
        MAIN_PROCESS = config['main_process']
    if 'model' in config:
        CONF_MODEL = config_path_prefix + config['model']
    if 'map' in config:
        CONF_MAP = config_path_prefix + config['map']
    else:
        CONF_MAP = None
    if args.trace_file:
        TRACE_FILE = args.trace_file
    elif 'trace_file' in config:
        TRACE_FILE = config_path_prefix + config['trace_file']
    else:
        if args.type == "offline" or args.type == "offline-test":
            # TODO Make this occur at the right point so that I don't have to repeat the header!!
            print("+++++++ VARANUS +++++++")
            print("++++ version " + str(VERSION_NUM) + " +++")
            print("++++ Matt Luckcuck ++++")
            varanus_logger.error("No Trace File given. Trace File is required for offline Runtime Verification.")
            quit()

    if 'name' in config:
        CHECK_NAME = config['name']
    if 'common_alphabet' in config:
        COMMON_ALPHA = config['common_alphabet']
    if 'mode' in config:
        MODE = config['mode'] # strict or permissive
        # TODO Check the mode is valid
    else:
        MODE = "permissive"
if args.name:
    CHECK_NAME = args.name
elif CHECK_NAME is None:
    CHECK_NAME = "scenario x"

MODEL = args.model
MAP = config_path_prefix + args.map
TYPE = args.type
SPEED_CHECK = args.speed

if args.log_path:
    LOG_PATH = args.log_path + "/"
else:
    LOG_PATH = "log/"

# TODO check and warn for incompatible params

################
# set to the name of the scenario
logFileName = CHECK_NAME
log_level = logging.DEBUG

if not os.path.exists("log"):
    os.mkdir("log")

varanus_logger = logging.getLogger("varanus")
varanus_logger.setLevel(log_level)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print(LOG_PATH)
print(TYPE)

fileHandler = logging.FileHandler(
    LOG_PATH + "varanus-" + TYPE + "-" + logFileName + "-" + time.strftime("%Y_%m_%d-%H:%M:%S") + ".log")

fileHandler.setFormatter(formatter)

varanus_logger.addHandler(fileHandler)

varanus_times = Time_Store()

def preprocess():
    varanus_logger.info("Preprocessing...")
    varanus_logger.info("Preprocessing: pass")
    pass

def run(check_type):

    if check_type == "offline":
        t0 = time.time()
        mon = Monitor(CONF_MODEL, CONFIG_FILE, CONF_MAP, old_version=True)
        mon._run_offline_traces_interate(MAIN_PROCESS, TRACE_FILE)
    elif check_type == "online":
        t0 = time.time()
        t0 = time.time()

        varanus_logger.debug(CONF_MAP)
        if CONF_MAP is not None:
            mon = Monitor(CONF_MODEL, CONFIG_FILE, CONF_MAP, MODE)
        else:
            mon = Monitor(CONF_MODEL, CONFIG_FILE, None, MODE)
        if COMMON_ALPHA:
            mon.build_state_machine(MAIN_PROCESS, COMMON_ALPHA)
        else:
            mon.build_state_machine(MAIN_PROCESS)
        build_end = time.time()

        #mon = Monitor(MODEL, CONFIG_FILE, MAP)
        #mon.run_online_traces_accumulate(IP, PORT, timeRun=False)
        mon.run_online_websocket(IP, PORT)
    elif check_type == "sm-test":  # This is temporary, for testing the state machine
        print("main process = " + MAIN_PROCESS)
        t0 = time.time()
        mon = Monitor(CONF_MODEL, CONFIG_FILE, MAP)
        build_start = time.time()
        mon.build_state_machine(MAIN_PROCESS)
        build_end = time.time()

        check_start = time.time()
        mon.run_state_machine_test(MAIN_PROCESS)
        check_end = time.time()
    elif check_type == "stress_test":
        varanus_logger.info("+++ Running Stress Test +++")
        stress_events = config["stress_events"]
        stress_reps = config["stress_repetitions"]
        varanus_logger.info("Events: " + str(stress_events))
        varanus_logger.info("Repetitions: " + str(stress_reps))

        t0 = time.time()
        if CONF_MAP is not None:
            mon = Monitor(CONF_MODEL, CONFIG_FILE, CONF_MAP, MODE)
        else:
            mon = Monitor(CONF_MODEL, CONFIG_FILE, None, MODE)
        build_start = time.time()
        if COMMON_ALPHA:
            mon.build_state_machine(MAIN_PROCESS, COMMON_ALPHA)
        else:
            mon.build_state_machine(MAIN_PROCESS)
        build_end = time.time()

        continue_monitoring = mon.check_monitorable(MAIN_PROCESS, ALPHABET, set(COMMON_ALPHA))

        if continue_monitoring:
            varanus_logger.error("+++ starting monitoring against" + MAIN_PROCESS + " +++")
            check_start = time.time()
            mon.run_offline_stress_test(MAIN_PROCESS, stress_events, stress_reps)
            check_end = time.time()
        else:
            varanus_logger.error("+++ " + MAIN_PROCESS + " is not monitorable ABORTING +++")
            check_start = time.time()
            check_end = time.time()

        varanus_times.add_time("build", build_end - build_start)
        varanus_times.add_time("check", check_end - check_start)


    elif check_type == "offline-test":  # temp for testing upgrade of offline mode
        varanus_logger.info("+++ Running Offline Test +++")
        t0 = time.time()

        varanus_logger.debug(CONF_MAP)
        if CONF_MAP is not None:
            mon = Monitor(CONF_MODEL, CONFIG_FILE, CONF_MAP, MODE)
        else:
            mon = Monitor(CONF_MODEL, CONFIG_FILE, None, MODE)
        build_start = time.time()
        if COMMON_ALPHA:
            mon.build_state_machine(MAIN_PROCESS, COMMON_ALPHA)
        else:
            mon.build_state_machine(MAIN_PROCESS)
        build_end = time.time()

        continue_monitoring = mon.check_monitorable(MAIN_PROCESS, ALPHABET, set(COMMON_ALPHA))

        if continue_monitoring:
            varanus_logger.error("+++ starting monitoring against" + MAIN_PROCESS + " +++")
            check_start = time.time()
            mon.run_offline_state_machine(MAIN_PROCESS, TRACE_FILE)
            check_end = time.time()
        else:
            varanus_logger.error("+++ " + MAIN_PROCESS + " is not monitorable ABORTING +++")
            check_start = time.time()
            check_end = time.time()

        varanus_times.add_time("build", build_end - build_start)
        varanus_times.add_time("check", check_end - check_start)

    # mon.run_online('127.0.0.1', 5044)
    # mon.run_online_websocket('127.0.0.1', 8080)
    mon.close()
    end_time = time.time()

    varanus_times.add_time("total", end_time - t0)

    #return times # probably not needed anymore


def log_speed(name, time, type):
    file_name = LOG_PATH + "varanus-" + TYPE + "-speed-check-" + name + ".csv"

    # If the file doesn't exist, open and close it -_-
    if not exists(file_name):
        output_file = open(file_name, "a")
        output_file.close()

    # Read the file to the end to get how many runs it has in it
    output_file = open(file_name, "r")
    csv_read = csv.reader(output_file, delimiter=',', quotechar='"')
    run_num = 0
    for run in csv_read:
        run_num += 1
    output_file.close()

    # Write the number of runs +1 into the file, with the time.
    output_file = open(file_name, "a")
    csv_write = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    run_num += 1
    csv_write.writerow(["Run" + str(run_num), time])
    output_file.close()





if __name__ == "__main__":
    print("+++++++++++++++++++++++")
    print("+++++++ VARANUS +++++++")
    print("++++ version " + str(VERSION_NUM) + " +++")
    print("++++ Matt Luckcuck ++++")
    print("+++++++++++++++++++++++")
    print("")

    varanus_logger.debug("Varanus Running v" + str(VERSION_NUM))

    varanus_logger.info("+++ Testing " + logFileName + " +++")

    preprocess()

    run(TYPE)

    print(varanus_times.times)

    print("")
    print("")
    # TODO make this print more clearly if the monitor found an error or not
    times = varanus_times.times
    extra_info = varanus_times.extras
    if 'build' in times and 'check' in times:
        varanus_logger.info("+++ Build Time: \t\t\t" + str(times['build']) + "s +++")
        varanus_logger.info("+++ Check Time: \t\t\t" + str(times['check']) + "s +++")
    if "avg_transition" in times:
        varanus_logger.info("+++ Average Transition Time: \t" + str(times["avg_transition"]) +"s ("+ str(extra_info["num_events"]) +" events) +++")
    varanus_logger.info("+++ Total Time: \t\t\t" + str(times['total']) + "s +++")


    varanus_logger.debug("Varanus Finished")

    if SPEED_CHECK == True:
        log_speed(CHECK_NAME, times['total'], TYPE)
