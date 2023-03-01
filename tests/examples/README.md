## Test examples

### Checking substrings in responses

To verify if particular phrase occurred in the response, there are two methods possible:

- simple check

```python
if "CREG" in test.dut.at1.last_response:
```
	
```python	
if "SIM PIN" in test.dut.at1.last_response:
	pass
```

  

- regular expression check

```python
import re
m = re.search("CREG", test.dut.at1.last_response)
```

for your convenience, you may also use regex flags:

```python
re.IGNORECASE
re.MULTILINE
re.DOTALL
```

full `re` module reference can be found under following link:

[https://docs.python.org/3/library/re.html](https://docs.python.org/3/library/re.html)

Please bear in mind, that built-in method **`send_and_verify`** uses DOTALL flag for response validation.


### URCs detection

Some URCs can be anticipated while others can happen anytime during test execution.

There's particularly one caveat in URCs detection - read operation is greedy so it will grab as much data as possible from the port. Every operation, that does the read, works in that way:

`read()`

`send_and_verify()`

`wait_for()`

if URC can happen only after some command, then recommended way to detect it, is to use following code snippet:

```python
 test.dut.at1.send("at+cops=2") 
 test.dut.at1.wait_for(".*CREG: 0.*", timeout=10)
```

if one wants to use send_and_verify, URC detection can be done as follows:


```python
test.dut.at1.send_and_verify("at+cops=2", "OK", timeout=30)
if "CREG: 0" in test.dut.at1.last_response:
	print("URC found, no need to wait")
else:
	print("URC not found yet, wait for it")
	test.dut.at1.wait_for(".*CREG: 0.*", timeout=10)
```

it is also worth to notice, that every command flushes `last_response` buffer. To suppress this behavior so the buffer can collect all responses, `append` parameter should be set to `True`:

```python
test.dut.at1.send_and_verify("at+cops=2", wait_for="CREG", timeout=60, append=True)
if "+CREG" test.dut.at1.last_response:
	test.log.info("URC arrived")
```



### Setting variable as test's attribute

`test` object is a container for various methods and parameters used during test execution. It is also possible to store own attributes in this object. Thanks to this mechanism, we can create object of our own class and use it in all test methods (`setup`, `run`, `cleanup`). We can also pass some variable in this way.

```python
test.my_test_server = MyServerClass(1.1.1.1, 1024)
```

```python
test.my_variable = 4
```



### Using available DSTL functions

Recommended way of importing available DSTL functions is presented below:

```python
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
```

All DSTL functions have `dstl_` prefix so it is always clear what kind of function is run.



### Print vs log

It is recommended to use `test.log` methods, e.g.:

```python
test.log.info("Info message") 
test.log.warning("Warning message") 
```

or

```python
dstl.log.info("Info message") 
dstl.log.warning("Warning message") 
```

instead of `print()` because in that case messages are also logged to a file except a console.

If messages are logged to console only, debugging will be harder.



### subprocess vs test.execute

Python has multiple ways of calling system commands. Particularly, `os` and `subprocess` modules can be mentioned for this purpose.

Unicorn has also built-in method based on subprocess call:

```python
test.os.execute()
```

or

```python
dstl.os.execute()
```

When Unicorn method is used, output will be properly logged. Otherwise, please remember about doing it explicitly in the test code to allow proper output analysis.



### Returning multiple values from functions

Python allows returning multiple values from a function as a tuple. Whenever it is suitable, feel free to use that possibility:

```python
return (True, message)
```



### Hard-coded paths

Please always try to avoid "hardcoded" paths, e.g.:

```python
work_dir = "c:\\work_dir"
```

and pass them from configuration file instead:

**local.cfg**

```python
work_dir = c:\work_dir
```

**test.py:**

```python
work_dir = test.work_dir
```
