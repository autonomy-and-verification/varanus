# State Machine Tests
#### Matt Luckcuck 2023/2024

This is where I am testing the CSP state machine, build by Fatma, as I integrate it into the main Varanus system. 

The config file expects a csp model and some traces (so far)

The traces file is a file with a JSON object on each line, which must contain the "topic" and "data" fields. If there is no data (i.e. the channel is untyped) then use "data": null. Note: do not make null into a string, or it will assume that the string "null" is the parameter being passed.
