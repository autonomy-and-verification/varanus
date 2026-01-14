# Varanus 0.9.4
### Matt Luckcuck
### Runtime Verification Toolchain using CSP and FDR

Varanus is a Runtime Verification (RV) toolchain for checking a program is obeying its specification. The specification must be written in Communicating Sequential Processes (CSP) and is assumed to parse correctly. Varanus listens to the events produced by a System Under Analysis (SUA), and checks that these events form a valid trace for the CSP specification.



## The Name

I chose the name _Varanus_ for two reasons:

1. Varanus is the genus of [Monitor Lizards](https://en.wikipedia.org/wiki/Monitor_lizard)
2. I have a poor sense of humour.

## Prerequisites

Varanus has been built and (only) tested on Ubuntu 19.10/20.04 using Python 2.7.17/18

### Python

Varanus is written using Python 2.7 because it uses FDR4 to parse and compile CSP specifications, and FDR4's Python interface 
is not compatible with Python 3.

* yaml package `pip install pyyaml` or `pip2 install pyyaml`
* websocket package `pip install websocket-client` or  `pip2 install websocket-client`

### FDR

Varanus assumes a pre-existing installation of [FDR4](https://cocotec.io/fdr/). This used to parse the CSP and check for monitorability. 

From the [FDR](https://cocotec.io/fdr/) website (accessed: 2020-07-08), install using:
```bash
sudo sh -c 'echo "deb http://dl.cocotec.io/fdr/debian/ fdr release\n" > /etc/apt/sources.list.d/fdr.list'
wget -qO - http://dl.cocotec.io/fdr/linux_deploy.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install fdr
```

#### FDR License

To quote from the FDR website
"All use of FDR require a license, however, you do **not** need to purchase a license if you are engaged in normal academic activity."

A free academic license is available from the license dialogue, when starting FDR. License details can be found on the [FDR Licensing Webpage](https://cocotec.io/fdr/licensing.html)


## Usage

Varanus is a terminal program within the `varanus/varanus-python` directory.

The basic usage is to run `varanus.py` passing a parameter that indicates either `online` or `offline` Runtime Verification, and a parameter that is the filepath of a `config` file (which, in turn, will point Varanus at the CSP model and System Under Analysis).

The basic workflow is:
 * Write a CSP specification for the System Under Analysis
 * Build the config file to point Varanus at the System Under Analysis and the CSP  specification (and some other parameters)
 * Run Varanus on the config file, telling it if it should do online or offline RV (if it's offline then the 'system' it is monitoring will be a trace file, also written separately.)

```bash
usage: varanus.py [-h] [-n NAME] [-l LOG_PATH]
                  {offline,online,sm-test,offline-test,stress-test,build-only}
                  config

positional arguments:
  {offline,online,sm-test,offline-test,stress-test,build-only}
                        The type of action or check for Varanus to perform.
  config                The location of the config file.

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Override the config file's name. This is the name of
                        the check and therefore name of the log file.
  -l LOG_PATH, --log_path LOG_PATH
                        Override the default log path.
```

Since Varanus 0.9.0 the parameters can be set in the config file, and some can be overridden at the command line.

* `logFileName` is the name of the file to which Varanus will log its run
* The parameters passed to the `Monitor()` constructor are the location of the model's main file and a JSON file containing a map of events in the SUA to events in the model (if these are different)
* `_run_offline_traces_single()` performs offline RV, it takes the file path to a JSON file containing the trace to be checked. This method checks the whole trace in one go.
* `run_online_traces_accumulate()`performs online RV, it takes the IP address and port number of a socket connection as parameters. This method checks traces incrementally, adding each event it receives to the trace and checking it. This method assumes there is a socket connection for it communicate with (in the MASCOT example, this is `varanus/mascot-test/dummy_mascot_socket.py`)
 - Adding the `timeRun=True` parameter to this method will collect timing information for each run.

### First Time Run

When running Varanus for the first time, you will receive a message saying that FDR requires a licence. As mentioned above, "All use of FDR require a license, however, you do not need to purchase a license if you are engaged in normal academic activity." But a free academic license is available from the license dialogue, when starting FDR.

Run `sudo fdr4` to start FDR, select the academic licence and add your name and an email address, to register for the licence. If this works, FDR will open, but you can close this and continue to use Varanus.

### Config File

The config file sets the following parameters:

* `alphabet`: the alphabet of the CSP process used as the monitor oracle
* `common_alphabet`: the alphabet of the System Under Analysis
* `model`: the filepath (relative to the config file) of the CSP model
* `main_process`: the name of the CSP process used as the oracle, which should exist in the `model`. For quick tests, this can be a simple CSP process written directly in to the parameter (e.g. `main_process: a -> b -> SKIP`) but the channels used have to exist in `model`.
* `name`: the name of the check or test being performed, this is used in the names of the log files
* `mode` (optional): there are two modes "strict", where Varanus will abort if an event from the System Under Analysis is not available in the current state of the model; and "permissive", where Varanus will ignore events from the System Under Analysis that are not available in the current state of the model (it will stay in the current state).
* `trace_file` (optional): the trace that Varanus should check against the model. This is only used for offline Runtime Verification.

### Quick Check

As a quick check that Varanus is installed correctly, you can enter the `varanus` root directly and run `python varanus-python/varanus.py offline rosmon-test/hibye.yaml` (assuming your `python` command points to Python 2.x) to run a very simple check on a simple process. If all is well, you should see `INFO:varanus:Trace file finished with no violations` at the end of the output to the terminal. 

Lets look at the config file we've just checked:

```yaml
---
alphabet: [hello, goodbye]
common_alphabet: [hello,goodbye]
main_process: "HI_BYE"
model: "hi_bye.csp"   
trace_file: "hello_goodbye.json"
name: "hi_bye_test"
mode: "strict"
```

This is pointing Varanus at the `hi_bye.csp` file (`model`) and making it check the `main_process`, `HI_BYE`, against the `trace_file`, `hello_goodbye.json`.

The trace file is very simple, it only contains two events:

``` json
{"topic": "hello", "data": null, "time" : 0}
{"topic": "goodbye", "data": null, "time" : 1}
```

Here, `hello_goodbye.json` is telling us that the System Under Analysis said "hello" and then "goodbye". Varanus has checked that the `HI_BYE` process specifies that this is acceptable behaviour.

Now lets look at the `HI_BYE` process itself:

```
channel hello, goodbye

HI = (hello -> HI [] goodbye -> SKIP)
BYE = goodbye -> SKIP

HI_BYE = HI [|{|goodbye|}|] BYE
```

This CSP specification introduces two `channels`, `hello` and `goodbye`. We can see that the `HI_BYE` process is defined by the parallel composition of the `HI` and `BYE` processes, where they must synchronise on the `goodbye` channel (meaning that they must perform `goodbye` at the same time). 

`HI` will allow any number of `hello` events, because it will recurse after performing `hello`, but if it performs `goodbye` then it will terminate. the `BYE` process is much simpler, it will just perform `goodbye`. 

This means that the trace in `hello_goodbye.json` is valid, because `HI_BYE` can perform one `hello` followed by one `goodbye` event. 



## Generic Components

* `event_converter.py`
  - Reads the event map JSON file, passed to the `Monitor()` constructor, to convert incoming SUA events to model events.
* `fdr_interface.py`
  - Connects Varanus to FDR. Based on FDR example file from https://cocotec.io/fdr/manual/_downloads/ffcc2113bd60df5a33677f5bbe5193da/command_line.py and modified.
* `system_interface.py`
  - Connects the monitor to the system being monitored.
* `monitor.py`
  - Controls the monitoring program.

## Specific Components

* `mascot_event_abstractor.py`
  - Implements `EventConverter` for the MASCOT example

* `event_map.json`
  - Provide a map from the events in the MASCOT example to the events in the model

## Troubleshooting

Here are some troubleshooting tips for problems with Varanus itself.

If you have problems installing or running **FDR4** please check the [FDR Troubleshooting](docs/fdr-troubleshooting.md) document.

## Cannot Install FDR: Depends: libpng12-0 but it is not installable

Using the instructions from: https://www.linuxuprising.com/2018/05/fix-libpng12-0-missing-in-ubuntu-1804.html

The instructions below work for **Ubuntu 22.10, 22.04, 21.10 or 20.04** (for 18.04, check https://www.linuxuprising.com/2018/05/fix-libpng12-0-missing-in-ubuntu-1804.html )

```
sudo add-apt-repository ppa:linuxuprising/libpng12
sudo apt update
sudo apt install libpng12-0
```

## Cannot run FDR: error while loading shared libraries: libtinfo.so.5: cannot open shared object file: No such file or directory

It seems this can just be installed: `sudo apt-get install libtinfo5`

## Cannot run FDR: Could not connect to FDR licensing server; please check your internet connection

This error happens on the License Application dialogue, when trying to validate the license.
Some Linux distributions have moved the TLS certificate store, and FDR cannot find it, so it can't connect. FDR 4.2.7 says it fixes an issue with not being able to connect to the licensing server, but this error still sometimes appears.

The fix that seems to work is to copy the TLS certificates to the location that FDR is expecting them to be at:
```
sudo mkdir -p /etc/pki/tls/certs/
sudo cp /etc/ssl/certs/ca-certificates.crt /etc/pki/tls/certs/ca-bundle.crt
```

## ImportError: libpython2.6.so.1.0: cannot open shared object file: No such file or directory

**Found with Python 2.7.18 and FDR 4.2.7**

If you try to run `Varanus` and get `ImportError: libpython2.6.so.1.0: cannot open shared object file: No such file or directory` this is because FDR's API is trying to use Python 2.6 and the library isn't available.

Here, the workaround uses the Python 2.7 version of this library, aliasing it to the Python 2.6 version.

Make sure that you have `libpython2.7.so.1.0` installed (it should be at `/usr/lib/x86_64-linux-gnu/libpython2.7.so.1.0`). If you do not, then you should be able to install it using:

```bash
sudo apt install python2.7-dev
```

When you are sure the library is installed, run the following:

```bash
sudo ln -s /usr/lib/x86_64-linux-gnu/libpython2.7.so.1.0 \
/usr/lib/x86_64-linux-gnu/libpython2.6.so.1.0

```
which is modified from [Stack Exchange](https://askubuntu.com/questions/427884/libpython2-6-so-1-0-doesnt-exist), which adds a link from the missing `libpython2.6.so.1.0` to the existing `libpython2.7.so.1.0` file.







