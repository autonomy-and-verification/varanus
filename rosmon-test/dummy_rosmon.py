import websocket
import sys
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json

""" Reads the json file supplied in FILE and sends this to the monitor """

TCP_IP = '127.0.0.1'
TCP_PORT = "5088"
FILE = "hello_goodbye.json"

def main(argv):
    websocket.enableTrace(True)
    websockets_str =  "ws://" + TCP_IP + ":" + TCP_PORT

    print(websockets_str)
    ws = websocket.WebSocketApp(
        websockets_str,
        on_message = on_message,
        on_error = on_error,
        on_close = on_close,
        on_open = on_open)
    ws.run_forever()

def on_message(ws, message):
    print("+++ On Message " , message)
    print(type(message))

    # THIS FAILS FOR SOME REASON, IT CAN'T SCAN THE message
    json_dict = json.loads(str(message))
    if "error" in json_dict:
        print('The event ' + message + ' is inconsistent..')
    else:
        print('The event ' + message + ' is fine..')

def on_error(ws, error):
    print(error)

def on_close(ws):
    print('+++ Dummy MASCOT websocket closed +++')

def on_open(ws):
    print('+++ Dummy MASCOT websocket is open +++')
    def run(*args):
        telegram_file = open(FILE, "r")
        for line in telegram_file:
            if line not in ['\n', '\r\n']:
                ws.send(line)
                print("+++ Dummy MASCOT sent data: ", line)
            else:
                print("+++ Dummy MASCOT ignoring blank line: ", line)


        telegram_file.close()

        time.sleep(1)
        close(ws)
        print("thread terminating...")
    thread.start_new_thread(run, ())

def close(ws):
    ws.close()

if __name__ == '__main__':
    main(sys.argv)
