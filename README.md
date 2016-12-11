# Snap collector plugin - htcondor
This plugin collects metrics from the [HTCondor](https://research.cs.wisc.edu/htcondor/) distributed computing system's daemons.

It's used in the [Snap framework](http://github.com:intelsdi-x/snap).

1. [Getting Started](#getting-started)
  * [System Requirements](#system-requirements)
  * [Installation](#installation)
  * [Configuration and Usage](#configuration-and-usage)
2. [Documentation](#documentation)
  * [Collected Metrics](#collected-metrics)
  * [Examples](#examples)
3. [Releases](#releases)
5. [License](#license)
6. [Acknowledgements](#acknowledgements)

## Getting Started
### System Requirements 
* [HTCondor 8.4+ library and Python bindings](https://research.cs.wisc.edu/htcondor/downloads/)

#### For building:
* Python 2.7
* virtualenv
* [acbuild](https://github.com/containers/build)

### Operating systems
Developed and tested on [Scientific Linux 7](http://www.scientificlinux.org/), but should work on any platform supported by Snap and HTCondor.

### Installation
#### To build the plugin:
Get source from https://github.com/fifemon/snap-plugin-collector-htcondor

Create a Python virtualenv with Snap and HTCondor Python libraries:
```
$ virtualenv venv
$ source venv/bin/activate
$ pip install git+https://github.com/intelsdi-x/snap-plugin-lib-py
$ cp /usr/lib64/libpyclassad*.so venv/lib/
$ cp /usr/lib64/python2.7/site-packages/{classad,htcondor}.so venv/lib/python2.7/site-packages/
```

Build the plugin container image by running make:
```
$ make
```

### Configuration and Usage
1. Set up the [Snap framework](https://github.com/intelsdi-x/snap/blob/master/README.md#getting-started)
2. Load the plugin:
```
$ snaptel plugin load snap-plugin-collector-htcondor-linux-x86_64.aci
```


## Documentation

### Collected Metrics
This plugin has the ability to gather the following metrics:

Namespace | Description (optional)
----------|-----------------------
/fifemon/htcondor/collectors/[Name]/[stat]/value          | Collector classad statistics
/fifemon/htcondor/hads/[Name]/[stat]/value                | HAD classad statistics
/fifemon/htcondor/masters/[Name]/[stat]/value             | Master classad statistics
/fifemon/htcondor/negotiators/[Name]/[stat]/value         | Negotiator classad statistics
/fifemon/htcondor/schedds/[Name]/[stat]/value             | Schedd classad statistics
/fifemon/htcondor/startds/[Name]/[stat]/value             | Startd classad statistics

### Examples
This is an example running htcondor and writing data to a file. It is assumed that you are using the latest Snap binary and plugins.

The example is run from a directory which includes snaptel, snapteld, along with the plugins and task file.

In one terminal window, open the Snap daemon (in this case with logging set to 1 and trust disabled):
```
$ snapteld -l 1 -t 0
```

In another terminal window:
Load htcondor plugin
```
$ snaptel plugin load snap-plugin-collector-htcondor-linux-x86_64.aci
```
See available metrics for your system
```
$ snaptel metric list
```

Create a task manifest file (e.g. `htcondor-file.yaml`):    
```yaml
---
  version: 1
  schedule:
    type: "simple"
    interval: "30s"
  max-failures: 10
  workflow:
    collect:
      metrics:
        /fifemon/htcondor/collectors/*/RecentDaemonCoreDutyCycle/value: {}
      config:
        /fifemon/htcondor:
          pool: "mycollector.example.com"
      publish:
        - plugin_name: "file"
          config:
            file: "/tmp/htcondor_metrics.log"
```
*`pool` must point to an actual HTCondor collector!*

Load file plugin for publishing:
```
$ snaptel plugin load snap-plugin-publisher-file
Plugin loaded
Name: file
Version: 3
Type: publisher
Signed: false
Loaded Time: Fri, 20 Nov 2015 11:41:39 PST
```

Create task:
```
$ MYTASK=$(snaptel task create -t htcondor-file.yaml | awk '/ID:/ {print $2}')
```

Watch metrics:
```
$ snaptel task watch $MYTASK 
Watching Task (8193d88d-91a3-4268-bcca-cac6096b6de4):
NAMESPACE                                                                                DATA                    TIMESTAMP
/fifemon/htcondor/schedds/schedd1.example.com/RecentDaemonCoreDutyCycle/value            0.004873894740515361    2016-12-11 16:12:18.6623690
12 -0600 CST
/fifemon/htcondor/schedds/schedd2.example.com/RecentDaemonCoreDutyCycle/value            0.008208892675616974    2016-12-11 16:12:18.6623690
12 -0600 CST
/fifemon/htcondor/schedds/schedd3.example.com/RecentDaemonCoreDutyCycle/value            0.005034234083056144    2016-12-11 16:12:18.6623690
12 -0600 CST
/fifemon/htcondor/schedds/schedd4.example.com/RecentDaemonCoreDutyCycle/value            0.004880455175492404    2016-12-11 16:12:18.6623690
12 -0600 CST
/fifemon/htcondor/schedds/schedd5.example.com/RecentDaemonCoreDutyCycle/value            0.004921509346445974    2016-12-11 16:12:18.6623690
12 -0600 CST
```

Stop task:
```
$ snaptel task stop $MYTASK
Task stopped:
ID: 8193d88d-91a3-4268-bcca-cac6096b6de4
```

## Releases

### Version 1

Initial alpha release. Collects basic stats (equivalent of `condor_status -l`). 

### TODO

* Tests and error handling
* Cleanup/refactor collect loops
* Collect job metrics (aggregate `condor_q` results)


## License
[Snap](http://github.com:intelsdi-x/snap), along with this plugin, is an Open Source software released under the Apache 2.0 [License](LICENSE).

## Acknowledgements
* Author: [@retzkek](https://github.com/retzkek)
