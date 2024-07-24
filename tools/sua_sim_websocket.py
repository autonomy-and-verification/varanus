import argparse
import websocket
import logging
import sys
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json

""" Reads the json file supplied in FILE and sends this to the monitor """

DEFAULT_TCP_IP = '127.0.0.1'
DEFAULT_TCP_PORT = "5088"

def main(args):
    websocket.enableTrace(True)
    TCP_IP = args.ip
    TCP_PORT= args.port

    websockets_str =  "ws://" + TCP_IP + ":" + TCP_PORT

    sim_logger.debug(websockets_str)
    ws = websocket.WebSocketApp(
        websockets_str,
        on_message = on_message,
        on_error = on_error,
        on_close = on_close,
        on_open = on_open)
    ws.run_forever()

def on_message(ws, message):
    sim_logger.info("+++ On Message " + message)
    print(type(message))

    # THIS FAILS FOR SOME REASON, IT CAN'T SCAN THE message
    json_dict = json.loads(str(message))
    if "error" in json_dict:
        sim_logger.error('The event ' + message + ' is inconsistent..')
    else:
        sim_logger.info('The event ' + message + ' is fine..')

def on_error(ws, error):
    sim_logger.error(error)

def on_close(ws):
    sim_logger.info('websocket closed')

def on_open(ws):
    sim_logger.info('+++websocket open')
    def run(*args):
        telegram_file = open(args[0], "r")
        sim_logger.info("Simulating with File: " + args[0] )
        for line in telegram_file:
            if line not in ['\n', '\r\n']:
                print (type(line))
                print (line)
                ws.send(str(line))
                sim_logger.info("+++sent data: " + str(line))
            else:
                sim_logger.info("+++ignoring blank line: " + str(line))
        telegram_file.close()

        time.sleep(1)
        ws.send("sua-sim:complete")
        close(ws)
        sim_logger.info("thread terminating...")
    thread.start_new_thread(run, tuple([args.file]) ) #Python is a silly language

def close(ws):
    ws.close()

if __name__ == '__main__':
    print("+++++++++++++++++++++++")
    print("+++++++ System-Under-Analysis Simulator +++++++")
    print("+++++++ Varanus Tools +++++++")
    print("++++ Matt Luckcuck ++++")
    print("+++++++++++++++++++++++")
    print("")

    logging.basicConfig()
    sim_logger = logging.getLogger("sua-sim")
    sim_logger.setLevel(logging.DEBUG)

    ### Arguments###
    argParser = argparse.ArgumentParser()
    argParser.add_argument("ip", help="IP Address of the Varanus Monitor")
    argParser.add_argument("port", help="port of the Varanus Monitor")
    argParser.add_argument("file", help="Filepath of the log file to send to the Varanus Monitor",
                           )

    args = argParser.parse_args()

    main(args)
