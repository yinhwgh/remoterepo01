Tests development guide
=======================

## Introduction

Current repository stores Unicorn's test cases. In order to execute them, Unicorn test framework must be first downloaded, installed and properly configured. To setup the environment please follow the guide placed in the main Unicorn's [README.md<sup>1</sup>](#references) file. 
All instructions for running the test are also placed there.



## Getting familiar with test scripts

Test scripts are written in Python programming language. However, the main idea is to use primarily DSTL libraries and Unicorn core functions.
Such approach improves readability, maintainability, flexibility and portability of the test cases.

Implementation of the new tests should be handled according to process defined by [Unicorn related processes<sup>2</sup>](#references).

Test file should contain test class declaration that inherits BaseTest class. Following methods should be implemented inside test class: 
- **setup** - steps to be executed before test is run,
- **run** - actual test steps
- **cleanup** - executed at the end to restore initial state of all involved devices.

Minimal test file example is shown below:

```python
import unicorn
from core.basetest import BaseTest

class Test(BaseTest):
    def setup(test):
        pass
        
    def run(test):
        test.expect(True)
        
    def cleanup(test):
        pass        

if "__main__" == __name__:
    unicorn.main()
    
```

There are two core imports and class declaration. Every test class inherits the code from BaseTest class and implements three methods: `setup`, `run` and `cleanup`.
The last section 
```
if "__main__" == __name__:
```
allows executing the test file itself.


Please refer to [Test examples<sup>3</sup>](#references) for more details.



## Test workspace

When unicorn starts executing the test, it creates new directory, where it will keep all test related files. Example path to the workspace, when `demo.py` test is run is presented below:
```
C:\projects\unicorn\logs\demo_<timestamp>
```

Test object stores this path to allow test developers saving additional test artifacts. It can be accessed in the following way:

```
test.workspace
```


Initially, three log files are created in this location - `main` related to the core/startup events, `aux` which saves information about configuration and runtime debug logs, and `test` related to test events only.

```
demo_main.log
demo_aux.log
demo_test.log
```

`main.log` is created mainly for debugging purposes. In most cases there is no need to browse it if test run successfully.



## Logging

Test developer has access to few logging methods which may be used to report specific test events. 
Test object is equipped with built-in logger object - it is available under `test.log` name.
Please however bear in mind, that logging do not intrinsically impact test result (e.g. logging `error` will not cause test to fail).
Means to evaluate test steps and to set test verdict are described in chapter: [Test result evaluation](#test-result-evaluation)


Logging methods that can be commonly used in test development are:

```
test.log.debug("This is a debug!")
test.log.info("This is an info!")
test.log.warning("This is a warning!")
test.log.error("This is an error!")
test.log.critical("This is a critical!")
```

and above and beyond:
```
test.log.step("Step in the test")
```

- debug level - should be used to report non-relevant events, useful mainly during test development
- info - method to be commonly used for all regular test actions 
- warning - events that may affect test result or unexpected conditions that do not fail the test
- error - events that are important in relation to test result
- critical - to log excepcionally important situations (errors)
- step - to split test actions into major sections.



## Debug, headless and quiet modes


Normally, Unicorn logs all events only to the files and `DEBUG` logs are hidden on the console. To enable printing `DEBUG` logs, Unicorn needs to be started with special switch:

```
unicorn tests\demo.py --debug
```

DEBUG mode is particularly useful when writing new tests or analyzing problems with the framework itself.

Headless mode on the other hand limits prints coming to the console - it is especially useful for automated environments based on Jenkins or TIM.
It slightly decreases usability but increases performance.

Headless mode can be configured either from command line:

```
unicorn tests\demo.py --headless
```

or in the global config file `global.cfg`:

```
log_headless=1
```



There is also `quiet` mode that can be configured either from command line or using `local.cfg` / `global.cfg` files. It suppresses printing test log events on the console.

This mode is designed for remote desktops, where printing big amounts of data on the console may be slowing down the user interface.

```
unicorn tests\demo.py --quiet
```

```
log_quiet=1
```




## Sleep

To hold the test, sleep method can be used as presented below:

```
test.sleep(10)
```

value provided in the brackets is time in seconds. During sleep, counter will be displayed on the console to allow tracking test execution.



## Accessing devices

Let's assume that user has entered following configuration in `config/local.cfg` file:

```
dut_usb_m = COM1
dut_usb_a = COM2
```

or equivalently on a POSIX based system:

```
dut_usb_m = /dev/ttyACM0
dut_usb_a = /dev/ttyACM1
```

Those mappings means that **dut_usb_m** device (DUT, USB, modem) is connected to **COM1** (or **/dev/ttyACM0**) physical port.
Similarly **dut_usb_a** application port is available at **COM2** (or **/dev/ttyACM1**).

Finally, logical mapping is being made:
```
dut_at1 = dut_usb_m
dut_at2 = dut_usb_a
```

which assigns **dut_at1** primary logical port to **dut_usb_m** physical port and correspondingly **dut_at2** secondary logical port to **dut_usb_a** physical port.
Such mechanism allows writing generic test cases, in which **dut_at1**, **dut_at2**, **r1_at1**, are the main interfaces to interact with the module - but still it is possible to switch modem and application ports by changing configuration file.

All configured device can be now accessed from the test code:
```
test.dut.at1
test.dut.at2
```



**Please notice the difference:** 

in config file parameter is named `dut_at1`. In tests it is recommended to use dot notation instead:

```
test.dut.at1
```

it means that `dut` device is an attribute of `test` and `at1` is an attribute of `dut`.  



## Serial interface API

Communication with serial devices is possible using several built-in methods:



### open

To force port opening if it was closed in the meantime or not open yet by other serial API call.

`open()`

```
test.dut.at1.open()
```



It is also possible to open the port automatically without any call. To enable this mechanism please add additional parameter `open` in serial port settings in `local.cfg`

```
dut_usb_m = COM10,open
dut_usb_m = COM10,115200,open
dut_usb_m = COM10,115200,8,N,1,10.0,no,no,no
```

for all parameters please use it in order:

```
 dut_usb_m = port, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts, dsrdtr
	 where:
	 	port - port name; Windows: "COM10", Linux: /dev/ttyACM0
	 	baudrate - 50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
            9600, 19200, 38400, 57600, 115200(default), 230400, 460800, 500000,
            576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000,
        bytesize - 8(default), 7, 6, 5
        parity - N(default), E, O, M, S
        	- N is None
          	- E is Even
          	- O is Odd
          	- M is Mark
          	- S is Space        
        stopbits -  1(default), 1.5, 2
        timeout - 10.0 (default)
 		xonxoff - yes, no(default)
 		rtscts - yes, no(default)
 		dsrdtr - yes, no(default)
```

by default interface timeout is set to 10 and can be defined for each interface separately under configuration file, but in case to change this value globally for all interfaces you can do that by:

```
at_timeout = 10
```

```
Example for using an inheritance tree:

devconfig/default.cfg
at_timeout = 10

devconfig/jakarta.cfg
at_timeout = 10

local.cfg
at_timeout = 10

local.cfg
dut_asc_0 = COM3,115200,8,N,1,10.0,no,yes,yes

test.py:
test.dut.at1.reconfigure(settings={"timeout": 16.0})
```

### close

To force port closing.

`close()`

```
test.dut.at1.close()
```



### send_and_verify

Basic command to send the message and verify if expected answer is matched, returns `True/False`. If expected message is not found `WARNING` will be logged.

```
send_and_verify(message, 
	expect="(?i)(\s|^)OK(\s|$)", 
	wait_for="(?i).*(OK|ERROR).*", 
	timeout=5, 
	silent=False,
	wait_after_send=0, 
	end="\r", 
	append=False,
	handle_errors=False,
	echo=False)
```

- `message` - message which is sent to the module e.g. "AT"
- `expect` - response which should finally be received from the module, e.g. "OK", if expected message is found function returns `True`, if not - `False`
- `wait_for` - response from the module which indicates when read should be stopped, in most cases module sends "AT", "ERROR", "0" or "4"
- `timeout` - maximum time to wait for terminator (``wait_for``)
- `silent` - if set to True, messages will not be logged
- `wait_after_send` - indicates that method should wait specific amount of time before starting read
- `end` - character which terminates message which is sent, e.g. "\r"
- `append` - if set to True, responses will be added to the `last_response` buffer
- `handle_errors` - when set to True, any critical error will not abort the test (e.g. lack of connection with the module). In such case errors can be handled internally by the test script.
- `echo` - enables echo checking for the command - so if a message is being sent (e.g. "AT"), this switch will indicate that module should also send back the command itself. 



examples: 
```
send_and_verify("at")
send_and_verify("at", "OK")
send_and_verify("at", ".*OK.*")
```

second argument of the method (`".*OK.*"`) is the expected answer. It may be just a simple string or RegEx phrase. In Unicorn tests, Perl-Compatible Regular Expressions should be used because checking is based on the built-in **re** module. To get familiar with it please visit following webpage:
[https://docs.python.org/3/library/re.html](https://docs.python.org/3/library/re.html)


in the next example, method will in addition wait, until value from `wait_for` attribute is found on the read buffer. Maximum wait time is defined with `timeout` attribute.  
```
send_and_verify("at", ".*OK.*", wait_for="OK", timeout=60)
```



### send

To simply send a message to the module, works with `string` and `byte` data types.

`send(message="at", wait_after_send=0.0, timeout=0, end="\r")`

examples: 

```
send("at")
send("a", end="")
send("at", timeout=10)
```



### read

Returns content of the read buffer (everything that came to the buffer and was not read yet using one of available methods). After read `last_response` buffer is flushed - unless optional `append=True` parameter was provided.

`read(append=False)`

examples: 

```
data = read()
```



### last_response

To read last message which module has sent back, we can query `last_response` attribute.

```
test.log.info(test.dut.at1.last_response))
```



However, read buffer is always flushed when any interface method is explicitly called.
If we want older messages to stay in the buffer, we can configure `send_and_verify` as follows:

```
send_and_verify("at", ".*OK.*", append=True)
```

**append=True** 

means *append the incoming data to the last_response buffer*.



### wait_for

This method waits for specific answer from the module which is expected to come, **timeout** value is the maximum time of waiting. Method returns `True` if awaited message was detected and `False` otherwise. If expected message is not found `WARNING` is also logged. Awaited message can be written as part of the string or as a Regular Expression phrase.

`wait_for(expect, timeout=60.0, append=False, greedy=True)`

WARNING: `wait_for` reads as much data as possible and flushes the read buffer after execution.
Therefore, if we are waiting for multiple URCs, it may happen that single 
`wait_for` instruction will read _ALL_ of them because of that greedy behavior!
To overcome this problem we should first check if URC was not already stored in the `last_response` variable.  

There are also other methods designed which may help to overcome this problem.


examples:

```
wait_for("OK", timeout = 90)
wait_for("SYSSTART", timeout = 90)
wait_for("OK", timeout=30, append=True)
```



### wait_for_strict

Similar to `wait_for` but will stop the read as soon, as expected message is found. It will not collect new messages after finding expected one so it is possible to catch multiple URCs one by one. It is equivalent to using `wait_for` method with optional parameter `greedy=False`



examples:

```
wait_for_strict("OK", timeout = 90)
wait_for_strict("SYSSTART", timeout = 90)
wait_for_strict("OK", timeout=30, append=True)

```



catching multiple URCs with `wait_for_strict`:

```
        test.dut.at1.send("at+cops=,,,0")
        test.dut.at1.wait_for_strict("CREG")
        test.dut.at1.wait_for_strict("CGREG")
        test.log.info(test.dut.at1.last_response)
        
        test.dut.at1.send("at+cops=,,,7")
        test.dut.at1.wait_for_strict("CREG")
        test.dut.at1.wait_for_strict("CGREG")
        test.log.info(test.dut.at1.last_response) 
```

equivalent to:

```
        test.dut.at1.send("at+cops=,,,0")
        test.dut.at1.wait_for("CREG", greedy=False)
        test.dut.at1.wait_for("CGREG", greedy=False)
        test.log.info(test.dut.at1.last_response)
        
        test.dut.at1.send("at+cops=,,,7")
        test.dut.at1.wait_for("CREG", greedy=False)
        test.dut.at1.wait_for("CGREG", greedy=False)
        test.log.info(test.dut.at1.last_response)
```



### verify_or_wait_for

This method will first try to check if message was already received and stored in `last_response` buffer and if not - it will start waiting for it.



```
verify_or_wait_for("CREG", timeout = 90)
```



```
        test.dut.at1.send_and_verify("at+cops=,,,0")
        test.dut.at1.verify_or_wait_for("CGREG")
        test.dut.at1.verify_or_wait_for("CREG")
        test.log.info(test.dut.at1.last_response)
        
        test.dut.at1.send_and_verify("at+cops=,,,7")
        test.dut.at1.verify_or_wait_for("CGREG")
        test.dut.at1.verify_or_wait_for("CREG")
```



```
        test.dut.at1.send_and_verify("at+cops=,,,0")
        test.dut.at1.wait_for("CGREG", append=True)
        test.dut.at1.wait_for("CREG", append=True)
        test.log.info(test.dut.at1.last_response)
        
        test.dut.at1.send_and_verify("at+cops=,,,7")
        test.dut.at1.wait_for("CGREG", append=True)
        test.dut.at1.wait_for("CREG", append=True)
```



### send_and_verify_retry

This function makes an attempt of calling `send_and_verify` procedure and tries `n` times. If during attempt the expected string is received 
then returns `True`, otherwise checks if string provided in 'retry_expect' parameter exists in module's last response, 
if yes then performs next attempt, otherwise returns False. Returns `False` if after `n` times the expected value is not received.

`send_and_verify_retry("AT+CIMI", expect="OK", retry=10, retry_expect="SIM busy", timeout=5, wait_after_send=0, end="\r", append=False)`

This method accepts all parameters, excluding `append` parameter, needed for `send_and_verify` procedure.



### send_and_read_binary

Send and read binary data from the port. Data could be of string or bytes type.

```
        Args:
            message(String | bytes): message which will be sent via serial
            size(int): number of bytes after which command ends, if 0 than will read till timeout
            timeout(int or float): timeout in seconds
            wait_after_send(float | int): adds sleep after sending command
            silent(bool): enable silent mode for this method
            end(String): end of line character(s)
        Returns:
            received(bytes): data read from the port
```

Simple example:

```python

data = test.dut.at1.send_and_read_binary("at")
test.log.info("DATA: {}".format(data))
```

Illustrative example of saving core dump file after sending AT command (may not work properly):

```python

bytes_read = 0
bytes_to_be_read = 102082382
packet_size = 1000

with open("coredump.bin", "wb") as file:
    remaining_size = bytes_to_be_read - bytes_read
    read_size = min(packet_size, remaining_size)
    data = device.at1.send_and_read_binary("AT^SABR=coredump,read,{}, {}".format(bytes_read, read_size), size=read_size)
    bytes_read += read_size
    file.write(data)
```



### send_file

Send file to serial port.

```
        Args:
            file(path): file path to be send, absolute or relative to unicorn directory
            wait_after_send(float | int): adds sleep after sending command
            timeout(int): reconfigures serial connection with custom write timeout
            silent(bool): enable silent mode for this method
            end(String): end of line character(s)
```

Illustrative example of sending module firmware via serial port (to present the idea, depends on module's capabilities!):

```python

dstl_restart(test.dut)
test.dut.at1.send("at^sfdl")

if test.dut.at1.wait_for_bytes(b"\x00", timeout=60):
    test.dut.at1.send_file("firmware.usf")

dstl_restart(test.dut)
```



### read_binary

Read binary data from RingBuffer till timeout or desired size received.

```
        Args:
            size(int): number of bytes to be received, 0 - wait till timeout
            timeout(int or float): timeout in seconds
            silent(bool): enable silent mode for this method

        Returns:
            bytes: received data
```



### wait_for_bytes

Method waits for the bytes sequence on the read buffer. When sequence is found True is returned.
Otherwise returns False. Information about the action is also logged beforehand.

```
        Args:
            wait_for(bytes): expected bytes sequence
            timeout(integer): maximum time to wait for the message
            silent(bool): enable silent mode for this method
        Returns:
            bool: True if pattern was matched, otherwise False
```



### reconfigure

Method to reconfigure serial connection with custom attributes. It accepts dictionary with serial's parameters as input:

`reconfigure(settings = {})`


```
reconfigure({
    "baudrate": 115200,
    "timeout": 1,
    "writeTimeout": 0.2,
    "xonxoff": False,
    "rtscts": False,
    "dsrdtr": False,
    "bytesize": 8,
    "stopbits": 1
})
```

User may provide all parameters from the list or choose only some of them like in the example below:

```
test.dut.at1.reconfigure({
    "timeout": 2,
    "writeTimeout": 0.2
})
```

list of the accepted parameters can be found in **pyserial** module documentation:
[https://pyserial.readthedocs.io/en/latest/pyserial_api.html](https://pyserial.readthedocs.io/en/latest/pyserial_api.html)



### settings

Is a dictionary which stores all initial configuration of the serial port (copy) . If some setting was changed (for example using `reconfigure` method), this dictionary can be used to compare the values or to revert the change.

```
test.log.info(test.dut.at1.settings)
```

```
{
    'baudrate': 115200, 
    'timeout': 0.02, 
    'writeTimeout': 10, 
    'xonxoff': False, 
    'rtscts': False, 
    'dsrdtr': False, 
    'bytesize': 8, 
    'parity': 'N', 
    'stopbits': 1
}
```



Actual values are stored under `_settings` attribute which can be also accessed although it is not recommended to do so:

```
test.log.info(test.dut.at1._settings)

{
    'baudrate': 115200, 
    'timeout': 0.02, 
    'writeTimeout': 10, 
    'xonxoff': False, 
    'rtscts': False, 
    'dsrdtr': False, 
    'bytesize': 8, 
    'parity': 'N', 
    'stopbits': 1
}
```



### reset

To restore original settings of the port that were set in the configuration (using copy stored in `settings` dictionary).

```
test.dut.at1.reset()
```

This method sets initial attributes of the connection, like `baudrate`, `timeout`, etc. It can be called at any time - but please be aware that module's port should be capable to deal with these settings afterwards.



### enable_tracing

Enable tracing of received data. After calling this function every incoming data will be saved to given file location.

```
        Args:
            file_path(path): path to file that will store traces
        Returns:
            bool: True if successful. Otherwise False.
```



### disable_tracing

Disable tracing of received data.

```
        Returns:
            bool: True if successful. Otherwise False.
```



### echo

It is possible to turn on constant echo checking for each sent command. To enable:

```
test.dut.at1.echo(True)
```

and to disable:

``````
test.dut.at1.echo(False)
``````

if 'echo' check should be done only for one call, specific argument can be provided to `send_and_verify` function:

```
test.dut.at1.send_and_verify('at', echo=True)
```



### terminator

Terminator is a value which is expected to be found at the end of the module response. In most cases it is `OK`or`ERROR` but some other characters are also valid terminators, e.g. `>`, `0`, or `4`.

By default, generic terminator value is:

```
r"(^|\r|\r\n|\n)(.*?OK|.*?ERROR.*?|0|4|>.*?)(\r|\r\n|\n|$)"
```

As other modules or supporting equipment like McTest may need other values, it is possible to override it, e.g.:

```
test.dut.at1.terminator = '.*>OK|>ERROR.*'
```

Terminator is a field to indicate that module response is finished and next method can be run. It is different concept than 'expected' response:

```
test.dut.at1.send_and_verify('at', expect='OK')
```



### Additional methods

Serial API provided by the `pyserial` module is not fully exposed and documented in the current guide - however all serial operations can be easily done without any restrictions.

`pyserial` object is stored under `connection` attribute, e.g.:

`test.dut.at1.connection`

Inquiring user may just check module's documentation and work with the underlying object.
Example of such operations:

```

test.dut.at1.connection.setDTR(True)
test.log.info(test.dut.at1.connection.dtr)
test.dut.at1.connection.setDTR(False)


```



### Hardware flow control

To set connection attributes, it is required to properly configure module and test environment. Example is presented below:

```
test.r1.at1.open()
test.r1.at1.send_and_verify("at^spow?")
test.r1.at1.send_and_verify("at^spow=2,1000,250")
        
test.log.info("Turn on flow control")
test.r1.at1.reconfigure({ 
            "baudrate":115200,
            "rtscts": True
})         
        
test.r1.at1.send_and_verify("at^spow?")

test.r1.at1.send_and_verify("at")

test.r1.at1.send_and_verify("at^spow=1,0,0")

```



### silent mode

With silent mode it is possible to suppress logging serial communication. Option may be used when module is sending big amounts of data or the messages are irrelevant for the test result.
It could be enabled permanently with serial class attribute or with additional parameter when calling method.

```python
# permanently enable silent mode / disable serial communication prints
test.dut.at1.silent(True)

...

# permanently disable silent mode / enable serial communication prints
test.dut.at1.silent(False)

...

# enable silent mode just for a single call
device.at1.send_and_verify("AT", silent=True)
```

Methods that support `silent` attribute are: 
[send_and_verify](#send), [send](#send), [read](#read), 
[wait_for](#wait_for), [send_and_read_binary](#send_and_read_binary), 
[send_file](#send_file), [read_binary](#read_binary), [wait_for_bytes](#wait_for_bytes)



### handle_errors mode

In this mode every error that could occur during serial method call will be handled and turned into `warning`.

With this mode it is possible to avoid situation when test is aborted due to `DEVICE_ERROR` error code (e.g. module stays in power saving mode and is not responding).

```
device.at1.send_and_verify("AT", handle_errors=True)
```



Methods that support `handle_errors` attribute are: 
[send_and_verify](#send), [send](#send), [read](#read), 
[wait_for](#wait_for), [send_and_read_binary](#send_and_read_binary), 
[send_file](#send_file), [read_binary](#read_binary), [wait_for_bytes](#wait_for_bytes)



### append

There's an option to temporarily enable appending new messages to the buffer. 
Such option may be primarily useful when writing test that are awaiting for specific URC.

**WARNING:** Using this method may have side effects as it will store ALL incoming data in the `last_response` buffer. It may lead to incorrect speed of sending commands or cause buffer overflow. 

`append(option=True)`

To enable this option we should perform: `append(True)` method, e.g.:

```
test.dut.at1.append(True)
```

to disable:

```
test.dut.at1.append(False)
```

example below shows how the last_response buffer will be filled:

```
test.dut.at1.send_and_verify("ati", "OK")
test.dut.at1.append(True)
test.dut.at1.send_and_verify("at", "OK")
test.dut.at1.send_and_verify("at", "OK")
test.dut.at1.append(False)
```

this is equivalent of the following code:

```
test.dut.at1.send_and_verify("ati", "OK")
test.dut.at1.send_and_verify("at", "OK", append=True)
test.dut.at1.send_and_verify("at", "OK", append=True)
```

test.dut.at1.last_response may now contain following entries:

```
ati
Cinterion
EHS6-A
REVISION 03.006

OK
at
OK
at
OK
```

after sending "ati" command, we enabled appending to the buffer 
so answers to two subsequent "at" commands were also added to the **last_response** variable.

However, please remember that it is test developer's responsibility to disable appending
in a proper time to avoid buffer overflow.





## OS API

Running commands on the local system can be easily done by interacting with `test.os` object.



### execute

To run the command and store the output. Returns full response.
```
ret = test.os.execute("ping localhost") 
```



### execute_and_verify

To run the command and verify if the output matches expected one:

```
ret = test.os.execute_and_verify("ping unknown.com", ".*Received.\=.0.*")
```



### last_response

Last command's response is always stored in `last_response` variable which can be analyzed after running the command:

```
test.os.last_response
```



### last_retcode

Last command's return code is stored in `last_retcode` variable:

```
test.os.last_retcode
```

Unicorn works with the built-in 32-bit Python interpreter.
As a consequence 64-bit Windows system tools may be run incorrectly because of internal system mechanisms.
Therefore, it is possible to override `wow64_redirection` parameter which by default is set to True and which allow running 64-bit applications. 

To temporarily disable WOW64 redirection we can provide optional parameter to the command like below:

```
test.os.execute("netsh mbn show interfaces", wow64_redirection=False) 
```

after execution, default behavior will be reverted.





## Accessing SIM card parameters

User can assign a SIM card to the device used in the test. To do it, **config/local.cfg** file must be filled with desired values, e.g.: 

```
dut_sim = E_6
```
this notation assigns `E_6` SIM card to the DUT. ID of the simcard is based on the entries from WebImacs database.

The same convention applies to remote devices, the only difference are prefixes (**r1**_sim, **r2**_sim).

To have the possibility of regular SIM attributes update basing on the data from WebImacs, `webimacs` plugin must be installed and enabled.

Please refer to documentation in `plugins/webimacs/README.md` how to perform these two steps.
Plugin works in online mode so on systems without Internet connection it will not work.
It simply searches for specific SIM id and updates the data in `config/simdata.cfg`.

When plugin is disabled `config/simdata.cfg` must be manually filled basing on entries from WebImacs. Please notice that attributes are not using CamelCase convention but are converted to lowercase words separated by underscores (recommended coding style for Python).

Example content of the file should look as below:

```
[E_6]
timestamp = 9999999999
cbst_max = None
cbst_max_isdn = None
entwickler_nr = None
fnur = None
gprs_apn = None
imsi = 260021063772177
int_data_nr = +48668168409
int_fax_nr = +48668168409
int_voice_nr = +48668168409
kartennummer_gedruckt = 8948022515097721776
lm_call_barring = true
dummy22 = None
lm_close_user_group = None
lm_gprs = None
lm_mms = None
lm_prepaid = None
lm_sms = None
lm_supplementary_service = None
sim_id = E_6
nat_data_nr = 668168409
nat_fax_nr = 668168409
nat_voice_nr = 668168409
nr_from_isdn_testnetz = None
pb_fd_capacity = None
pb_fd_nlength = None
pb_on_capacity = None
pb_on_nlength = None
pb_vm_capacity = None
pb_sm_nlength = None
pdu = None
pin1_net = 9999
pin1 = 9999
pin2 = 0667
umts_user = None
umts_password = None
gprs_user = None
gprs_apn_ipv6 = None
ip_address = None
lm_flat_data = None
lm_flat_voice = None
lm_flat_sms = None
simserverpath = None
cardinuseuntil = None
reserved = None
lm_camm = None
pb_ld_capacity = None
pb_en_capacity = None
pb_sm_capacity = None
pb_vm_writable = None
lte = true
lm_multiple_pdp_contexts = None
lm_clip = true
lm_clir = None
lm_colp = None
lm_call_forwarding = true
lm_multiparty = None
lm_aoc = None
lm_disable_pin = None
lm_fd_lock = None
lm_cpls = None
pb_mc_capacity = None
pb_dc_capacity = None
pb_rc_capacity = None
pb_vm_availability = None
over_the_air = None
lm_sals = None
lm_ccwa = true
lm_conference = None
gprs_apn_2 = None
gprs_apn_2_ipv6 = None
gprs_user_2 = None
lm_call_hold = None
pb_bn_available = None
cdma = None
pb_ld_available = None
pb_fd_available = None
lm_usim = true
pb_ec_available = None
pb_sn_available = None
pb_en_available = None
lm_csd_call = None
csd_nr = None
sca_int = +48602951111
sca_pdu = None
sms_anzahl = None
zyxel_dial = None
imsi_kurz = 177
umts = true
notice = None
pin2_net = 0667
lm_mailbox_inactive = False
bemerkungen_1 = None
bemerkungen_2 = None
imei = None
nat_fax_nr_ts61 = None
nat_fax_nr_ts62 = None
nat_data_nr_9k6_v32 = None
nat_data_nr_9k6_v110 = None
nat_data_nr_14k4_v34 = None
nat_data_nr_14k4_v110 = None
puk1 = 16636600
puk2 = 23412417
provider = Era (Pl)
umts_apn = internet
sca = +48602951111

```

To read PIN1 value of DUT's SIM (dut_sim), one should use following code:

```
pin_value = test.dut.sim.pin1
```

Then, example PIN entering code is shown below:

```
pin_value = test.dut.sim.pin1
test.dut.at1.send("at+cpin={}".format(pin_value))
```
or in one step:
```
test.dut.at1.send("at+cpin={}".format(test.dut.sim.pin1))
```

format method is recommended in Python because it ensures type conversion. This notation means that value of `test.dut.sim.pin1` will be put where the brackets `{}` are.



## Accessing test parameters

Every test configuration parameter can be accessed during test execution. It will be accessible from test object and the parameter name will be the same as in configuration files. Regarding parameters passed through command line it looks a little bit different.
Optional command line parameters should start with two hyphens and next keywords should be also separated with hyphen.

### Direct access

To directly read test attribute passed from the external configuration we can use following examples:

#### global.cfg
`global_parameter=1`

How to access in test:

`test.global_parameter`

#### local.cfg
`local_parameter=0`

How to access in test:

`test.local_parameter`

#### command line
`test_file.py --command-line-parameter=True`

How to access in test:

`test.command_line_parameter`



### get 

*Added in 5.2.0 version*

If some test attribute does not exist - for instance it was not set in the configuration file or not passed from the command line - test will crash because of `AttributeError` exception. To avoid such situation we can use safer option - method available under `test.get()`.

The syntax of this method is presented below:

```
my_value1 = test.get('global_parameter')
my_value2 = test.get('local_parameter')
my_value3 = test.get('command_line_parameter')
```

if parameter is not set, method will return `None` value.

It is also possible to provide default values for the method. In such case, if parameter is set it will be read and if not, default value will be returned.

```
my_value1 = test.get('global_parameter', 'foo')
my_value2 = test.get('local_parameter', 'bar')
my_value3 = test.get('command_line_parameter', 'baz')
```



## Test result evaluation

Test object has two important methods:
- `test.attempt()`
- `test.expect()`

which are used to perform and evaluate test actions.


### expect
Expect method checks if test step matches desired state, it simply evaluates if instruction in the brackets is `True` or `False`, e.g.:

```
test.expect(True)
test.expect(1 != 2)
test.expect(1 < 2)
test.expect(1 != 2 and 2 > 1)
```

`send_and_verify` is the main method that should be used to interact with all interfaces.
We can base on the fact, that this method returns `True` or `False` logical value 
and stores answers in` last_response` variable.

To perform test checks we may use presented options:

```
test.expect(test.dut.at1.send_and_verify("at", "OK"))
```

```
test.dut.at1.send_and_verify("at", ".*OK.*|.*ERROR.*")
test.expect("OK" in test.dut.at1.last_response)
```

similar convention can be used for `adb` type interface:
```
test.expect(test.dut.adb.send_and_verify('cat /etc/version', 'BOBCAT_XYZ')
```

`test.expect()` method accepts also additional parameter called `msg`. It is simply the message which will be printed if checked condition is False. 

Example:
```
test.expect(test.dut.adb.send_and_verify('cat /etc/version', 'BOBCAT_XYZ'), msg="Wrong version of the product in /etc/version file")
```



### attempt

Attempt method can be used when we try performing some action several times. Arguments are:

- method to call
- list of named arguments for this method
- `retry` - number of attempts

If condition is not fullfilled until last iteration is reached, test result is set to FAIL, e.g.:

```
test.attempt(test.dut.at1.send_and_verify, "at", timeout=60, retry=10)
```

In this example we are trying to send AT command ten times. If 10<sup>th</sup> iteration fail
whole test will fail. If method succeeds before reaching max counter it will be marked as PASSED.


For more details and examples please refer to [Unicorn Code documentation<sup>4</sup>](#references) and [Test examples<sup>3</sup>](#16-references): 
`examples/template_expect.py`
`examples/template_at.py`
`examples/template_dstl.py`





## Test sections

All test operations are allowed only in `setup`, `run` and `cleanup` methods
or functions/methods called directly from them, e.g.:

```
import unicorn
from core.basetest import BaseTest

class Test(BaseTest):
    def setup(test):
        pass
        
    def run(test):
        test.dut.at1.send("at+cfun=1,1")
        test.dut.at1.wait_for("SYSSTART", timeout = 90)

    def cleanup(test):
        pass        

if "__main__" == __name__:
    unicorn.main()

```

When creating new test, it is important to properly split its steps into these three sections.
Setup is used to do all preconditions, run to perform all crucial checks and cleanup to leave the device in the initial state.



## Device remapping

Standard serial interface used in the tests and DSTL functions is `test.dut.at1`. In order to use already existing tests and functions, though, with a different interface under `test.dut.at1` object, it is possible to create mapping which will substitute interfaces. Mechanism can be also used to dynamically change physical interface mapped to `test.dut.atX` alias.

Following command:

```
test.remap({'dut_at1': 'dut_mux_2'})
```

will replace existing configuration from `local.cfg` file (e.g. `dut_usb_m`) to the new one. So from this moment, all calls to`dut_at1` will be redirected to `dut_mux_2`.



Similarly, this code will first perform `dstl_detect` function on the interface read directly from the configuration file (`local.cfg`) and then, on a remapped interface.

```
from dstl.auxiliary.init import dstl_detect

dstl_detect(test.dut)

test.remap({'dut_at1': 'dut_mux_2'})
dstl_detect(test.dut)
```



## Internal execution of the test scripts

It is possible to execute another test script from the base one - the only restriction is that both tests cannot use the same resources. If the "child" test uses different devices or interfaces, then it can be run as is. Otherwise it is possible to remap test interfaces basing on the mechanism mentioned [above](#device-remapping) .

Method which is used for this purpose is named `perform`. Example which shows how to initialize such test is presented below:

```
test.perform("child_test.py") 
```

with device remapping using command line syntax:

```python
test.perform("child_test.py", '--map dut_at1=dut_mux_1') 
test.perform("child_test.py", '--map dut_at1=dut_mux_2')
test.perform("child_test.py", '--map dut_at1=dut_mux_3')
```

or by entering dictionary with the mapping:

```python
test.perform("child_test.py", {'dut_at1': 'dut_mux_1'}) 
test.perform("child_test.py", {'dut_at1': 'dut_mux_2'}) 
test.perform("child_test.py", {'dut_at1': 'dut_mux_3'})
```

All calls to `dut_at1` port will be changed to `dut_mux_1`, `dut_mux_2` and `dut_mux_3` respectively.

<u>Please notice, that both tests will be started in parallel.</u> 



To change default behavior and run tests in a sequence instead, please provide optional parameter `concurrent=False`.

```
test.perform("child_test.py", '--map dut_at1=dut_mux_1', concurrent=False) 
test.perform("child_test.py", '--map dut_at1=dut_mux_2', concurrent=False) 
test.perform("child_test.py", '--map dut_at1=dut_mux_3', concurrent=False)
```

or:

```
test.perform("child_test.py", {'dut_at1': 'dut_mux_1'}, concurrent=False) 
test.perform("child_test.py", {'dut_at1': 'dut_mux_2'}, concurrent=False) 
test.perform("child_test.py", {'dut_at1': 'dut_mux_3'}, concurrent=False)
```



After execution, test result is evaluated and treated as a regular check (`expect`) in the test. 



It is also possible to force wait for the child processes. To do so, test developer can use one of the possible options:

```
        test.perform("child_test.py", '--map dut_at1=dut_mux_1')
        test.perform("child_test.py", '--map dut_at1=dut_mux_2')
        test.perform("child_test.py", '--map dut_at1=dut_mux_3')
    
        test.sync()
```

in that case, `sync` method will force wait until all started processes finish. The other way, is to wait for particular processes:

```
        s1 = test.perform("child_test.py", '--map dut_at1=dut_mux_1')
        s1.sync()
        s2 = test.perform("child_test.py", '--map dut_at1=dut_mux_2')
        s2.sync()
        s3 = test.perform("child_test.py", '--map dut_at1=dut_mux_3')
        s3.sync()
```



## Prerequisites fulfillment

### test.require_plugin
Procedure checks if the required plugin is enabled, if not throws `PluginNotEnabled` exception and stops the test.

Example:
```
test.require_plugin("vision")
```



### test.require_package

Procedure Checks if the required package is available(installed), optionally checks package version also, if not throws `PackageMissing` exception.
Example:

```
test.require_package("request")
test.require_package("request", version="2.22.0")
```



### test.require_parameter

Method will check if optional parameter was entered either in `local.cfg` or as a command line parameter. If parameter is missing test will be aborted.

```
test.require_parameter("ip_server")
```





## Aborting test

When critical error occurs during testing and it becomes obvious that continuing test execution does not make sense,
it is possible to abort it.

There are few possible ways to do it: 
- with `test.expect(False, critical=True)` method
- with `test.fail()` method
- by raising exception

result of each method is slightly different so it's important to choose the proper one.



### test.expect

When test developer provides optional parameter `critical=True` to `test.expect` method it means that this particular test check is extremely important. 
This step must always pass to make testing process valid.
In such case, if condition in `test.expect` method evaluates to `False` test will be aborted.
This method will increase the counter of all test checks with the failed one.

Example:

```
var = 0
test.expect(var == 1, critical=True)
```



### test.fail

This method does the same action as the previous one. It will increase the counter of failed steps and immediately abort the test.

Example:

```
test.fail()
test.fail('Error occurred during execution')
```



### raise exception

Alternative option to stop testing is by raising exception from the test code.
It may be either user defined exception, built-in exception or generic exception.
However this method will not increase the counter of test checks so it may lead to `INCONCLUSIVE` result.


```
class MyModuleException(Exception):
    """Critical problem with my module"""
    pass

raise MyModuleException("Critical error occurred")
raise RuntimeError("Critical error occurred")
raise Exception("Critical error occurred")

```



## Threads

Under exceptional circumstances, there may be a need to perform multiple test actions in parallel. 
Unicorn gives such possibility by exposing `test.thread` method. Implementation is based on the Python's built-in module: [https://docs.python.org/3/library/threading.html](https://docs.python.org/3/library/threading.html) 
Mechanism creates new thread from the existing function or method, starts running it and also returns `threading.Thread` object.
Test developer can then interact with the thread if there's such a need.

Arguments for the thread are passed as consecutive values after function's or method's name.

Examples:
```
t1 = test.thread(test.dut.at1.send_and_verify, "at", expect="OK")
t2 = test.thread(test.os.execute, "ping google.com")
```

It is also possible to pass DSTL function into thread (creating DSTL functions is described in details under following link: [DSTL developer guide<sup>3</sup>](#references).):
```
from dstl.init import detect

t1 = test.thread(test.dut.detect)
t2 = test.thread(test.r1.detect)
```



Finally, we may force wait until threads synchronize before performing next actions. To do it we should call `join()` method:

```
t1.join()
t2.join()
```



## Setting KPIs

During test execution Unicorn collects KPI data that can be later analyzed by external systems.

This is additional mechanism layered over existing test and DSTL execution engines.

It is possible to enable/disable mechanism when starting the test or to suppress/resume at any time during test execution.

Possible options are listed below:

##### Command line call:

```
unicorn <test> --nokpi
```

##### global.cfg / local.cfg:

```
kpi_collect=0
kpi_collect=1
```

##### Test script:

```
test.kpi.enable()
test.kpi.disable()
```

##### DSTL function:

```
dstl.kpi.enable()
dstl.kpi.disable()
```



Each call of `test.expect` increases the counter of total checks. If checked condition is `True`, then it will also increase counter of passed checks.
This mechanism is working for all tests.

Additionally, user has ability to set optional test KPIs which will provide more information about test result. Example of such KPI is data throughput or duration of some operation in seconds.
There are two types of KPIs that can be set:

- bin (binary/boolean/integer) - KPI that evaluates to True or False, or Integer 0 or 1
- num (numerical) - KPI with some numerical value that can be represented as Integer or Float type variable


To store the value following instruction should be used:

```
test.kpi.store(name="num_kpi", type="num", value=6, device=test.dut)
test.kpi.store(name="bin_kpi", type="bin", value=True, device=test.dut)
```

following instructions will assign value `6` to KPI with name `num_kpi` and `True` to `bin_kpi`.
Statement `device=test.dut` will indicate, that KPIs are related to the specified device.


For binary KPIs user is able to define, number of passed result per number of opportunities. Fox example 4 steps have passed from 6 step which have been executed. In such case, there is no need to store the KPI in each step, there is possibility to store summarize KPI at the end of the test, user is able to store this value by using `total` parameter:

```
test.kpi.store(name="bin_kpi", type="bin", value=4, total=6, device=test.dut) 
```

It is also possible to set binary KPI directly from `test.expect` method.
To do so, name of the KPI should be provided as below:

```
test.expect(True, kpi="set_from_expect", device=test.dut)
```



### Timers

There's built-in simple mechanism to measure execution time of selected code blocks. To use it it is needed to call start and stop methods in the proper place:

```
test.kpi.timer_start(name, device)
test.kpi.timer_stop(name)
```

Measured time will be stored under provided `name` KPI.

In order to properly assign device to the KPI (either `dut` or `remote`) it is recommended to always provide its value as a parameter:

```
test.kpi.timer_start("ping_duration", device=test.dut)
test.kpi.timer_stop("ping_duration")
```

or alternatively in stop method:

```
test.kpi.timer_start("ping_duration")
test.kpi.timer_stop("ping_duration", device=test.dut
)
```

If test developer explicitly does not want to provide any device (e.g. if KPI is generic and not related to one single device), it should be specified as below:

```
test.kpi.timer_start("ping_duration", device=None)
test.kpi.timer_stop("ping_duration")
```



### Intermediate storage

In case there's a need to store some raw data which should be used for KPI collection by subsequent functions, there is separate namespace created solely for this purpose:

```
test.kpi.storage
```

test developer can assign any new parameter under this namespace, e.g.:

```
test.kpi.storage.my_first_temp_value = 5
test.kpi.storage.my_second_temp_value = 5
```

and finally:

```
my_overall_value = test.kpi.storage.my_first_temp_value + test.kpi.storage.my_second_temp_value
```



For more details and examples please refer to [Unicorn Code documentation<sup>4</sup>](#references) and [Test examples<sup>3</sup>](#16-references): 
`examples/template_kpi.py`



### Overriding weight of the expect instruction

When needed, it is possible to override weight of the `test.expect` method by providing optional parameter

**weight** like below:

```
test.expect(condition, weight=4)
```
In this case if condition is True, then counter of passed checks and counter of total checks will be increased by `4`.
Otherwise, only counter of total checks will be increased which will mean that 4 "checks" failed.
This option should be used for commands that accept multiple input parameters to indicate that every functionality related to every provided parameter passed or failed.



## Common patterns and recommended coding style

To get acquainted with solutions to common problems, built-in features or code snippets that may be useful in test scripts, please browse **[examples](examples/README)** directory. Feel free to add new example that may help other test developers. Additionally you may request adding example from core development team.

[examples/README.md](examples/README.md)



## Parameters/properties naming convention for Unicorn (special equipment)

Unicorn is test framework written in Python and uses snake case naming convention (all phrases are lower case and separated by underscore).

Table below shows examples how to translate parameters from camel to snake case naming convention.



| Pegasus property (CamelCase) | Unicorn property (snake_case) |
| ---------------------------- | ----------------------------- |
| embLinuxBuildSrvPort         | emb_linux_build_srv_port      |
| envModemLogMux               | env_modem_log_mux             |
| FtpServerPasswordIPv6        | ftp_server_password_ipv6      |
| embLinuxBuildApps            | emb_linux_build_apps          |
| ipServerSshPassword          | ip_server_ssh_password        |




## References
\[1] [Unicorn User guide](../README), unicorn/README.md <br>
\[2] [Unicorn Related processes](https://confluence.gemalto.com/display/GMVTIB/Unicorn+Related+processes), https://confluence.gemalto.com/display/GMVTIB/Unicorn+Related+processes <br>
\[3] [Test examples](../tests/examples/README), unicorn/tests/examples/ <br>
\[4] [Unicorn Code documentation](../../codedoc), unicorn/doc/codedoc.html <br>
\[5] [DSTL developer guide](../dstl/README), unicorn/dstl/README.md <br>
