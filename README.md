# Varanus 0.9.1
### Matt Luckcuck
### Runtime Verification Toolchain using CSP and FDR

Varanus is a Runtime Verification (RV) toolchain for checking a program is obeying its specification. The specification must be written in Communicating Sequential Processes (CSP) and is assumed to parse correctly. Varanus listens to the events produced by a System Under Analysis (SUA), and checks that these events are a valid trace of the CSP model using [FDR](https://cocotec.io/fdr/) (the CSP model checker).

### Papers

Varanus is an academic tool and therefore has been described in papers, which are also available in the 'papers' directory.

* _Monitoring Robotic Systems using CSP: From Safety Designs to Safety Monitors_, Matt Luckcuck, (Under Review) [arXiv](https://arxiv.org/abs/2007.03522)
 - Information about how to run the MASCOT example presented in the paper can be found in `varanus/mascot-test/README.md`

## The Name

Varanus is the genus of [Monitor Lizards](https://en.wikipedia.org/wiki/Monitor_lizard)

## Prerequisites

Varanus has been built and (only) tested on Ubuntu 19.10/20.04 using Python 2.7.17/18

### Python

Varanus is written using Python 2.7 (but compatibility with Python should only involve fixing some small syntax errors).

* yaml package `pip install pyyaml` or `pip3 install pyyaml`

### FDR

Varanus assumes a pre-existing installation of [FDR4](https://cocotec.io/fdr/).

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

```bash
usage: varanus.py [-h] [--model MODEL] [--map MAP] [-n NAME]
                  [--log_path LOG_PATH] [-t TRACE_FILE] [-s SPEED]
                  {offline,online,sm-test,offline-test} config

positional arguments:
  {offline,online,sm-test,offline-test}
                        The type of check to be performed
  config                The location of the config file

optional arguments:
  -h, --help            show this help message and exit
  --model MODEL         The location of the model used as the oracle.
  --map MAP             The location of the event map
  -n NAME, --name NAME  The name of the check and therefore name of the log
                        file
  --log_path LOG_PATH   The path of the log dir
  -t TRACE_FILE, --trace_file TRACE_FILE
                        The location of the trace file. Only used if
                        type='offline'
  -s SPEED, --speed SPEED Run 10 timed run and produce the times and mean.).
```

In Varanus 0.9.0 the parameters can be set in the config file, and some can be overridden at the command line.

* `logFileName` is the name of the file to which Varanus will log its run
* The parameters passed to the `Monitor()` constructor are the location of the model's main file and a JSON file containing a map of events in the SUA to events in the model (if these are different)
* `_run_offline_traces_single()` performs offline RV, it takes the file path to a JSON file containing the trace to be checked. This method checks the whole trace in one go.
* `run_online_traces_accumulate()`performs online RV, it takes the IP address and port number of a socket connection as parameters. This method checks traces incrementally, adding each event it receives to the trace and checking it. This method assumes there is a socket connection for it communicate with (in the MASCOT example, this is `varanus/mascot-test/dummy_mascot_socket.py`)
 - Adding the `timeRun=True` parameter to this method will collect timing information for each run.

## Generic Components

* `event_converter.py`
 - Reads the event map JSON file, passed to the `Monitor()` constructor, to convert incoming SUA events to model events.
* `fdr_interface.py`
 - Connects Varanus to FDR. Based on FDR example file from https://cocotec.io/fdr/manual/_downloads/ffcc2113bd60df5a33677f5bbe5193da/command_line.py and modified.
* `system_interface.py`
 - Connects the monitor to the system being monitored.
* `monitor.py`
 - Controls the monitoring program.
 - Should be generic, but the methods it currently provides may be a little specific.

## Specific Components

* `mascot_event_abstractor.py`
  - Implements `EventConverter` for the MASCOT example

* `event_map.json`
  - Provide a map from the events in the MASCOT example to the events in the model

## Troubleshooting

## ImportError: libpython2.6.so.1.0: cannot open shared object file: No such file or directory

**Found with Python 2.7.18 and FDR 4.2.7**

If you try to run `Varanus` and get `ImportError: libpython2.6.so.1.0: cannot open shared object file: No such file or directory` this is because FDR's API is trying to use Python 2.6 and the library isn't available.

With Python 2.7.18 I have used the following workaround

```bash
ln -s /usr/lib/x86_64-linux-gnu/libpython2.7.so.1.0 \
/usr/lib/x86_64-linux-gnu/libpython2.6.so.1.0

```
modified from [Stack Exchange](https://askubuntu.com/questions/427884/libpython2-6-so-1-0-doesnt-exist), which adds a link from the missing `libpython2.6.so.1.0` to the existing `libpython2.7.so.1.0` file.
