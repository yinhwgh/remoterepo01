Handling Embedded Linux userware (C/C++ applications)
============================================



## Requirements

Preparation and execution of Embedded Linux test scripts is a more complex procedure when compared to "regular" tests because it requires other systems which allow either cross-compilation of C and C++ applications on the fly from the sources or storing binary versions of such applications. 

In addition some type of interfaces which are used for communication with test devices are not enabled by default in Unicorn test framework so to allow using them it is needed to install supporting plugins, e.g: `adb` and `ssh`. 





## External systems

### Artifactory / ClearCase

Artifactory and ClearCase are storage systems on which binary versions of applications are stored. It is possible to use binary version of the Embedded Linux of the application only if it was prebuilt before the test and uploaded to this kind of storage.

Mass building procedure can be carried automatically when new firmware is released. On a dedicated Linux machine there is a job which installs new version of the SDK and then  builds all applications from the sources, one by one.



<TARTIFACTORY CONCEPT UNDER DEVELOPMENT >

```
artifactory__address = 
artifactory__username = 
artifactory__password = 
artifactory__token = 
```



### Linux build server

This is a dedicated Linux machine which cross compiles Linux application from the sources to the binary form. 

Such machine needs stable network connection and SSH server to be installed in order to allow communication with the test environment.

Operating system which is installed on this machine needs to be compatible with SDK of the product (e.g. Ubuntu Linux 18.04). Please refer to wireless module's specifications to get this information.

Please also notice that machine compatible with Bobcat SDK may not necessary be compatible with Kraken.



On order to setup this kind of machine please refer to the article:

https://confluence.gemalto.com/display/GMVTIB/Server+Setup+Kraken+Build+Server



Whole process of handling Linux applications is described on the confluence page:

https://confluence.gemalto.com/pages/viewpage.action?pageId=763066745





### Required plugins

#### adb

ADB plugin allows execution of commands on the module's Linux shell and file transfer to/from the module's filesystem.

If you install Unicorn on Linux please also make sure that Android platform tools are installed:

```
sudo apt update
sudo apt-get install android-tools-adb android-tools-fastboot

sudo adb start-server 
```

on Windows there is no need to install platform tools because they are included in the plugin.



Then please run:

###### Windows

```
unicorn\plugins\adb\install.cmd
```

###### Linux

```
unicorn/plugins/adb/install.sh
```



#### ssh

SSH plugin allows execution of the commands and file transfer from/the Linux build server.

Sources of the application are at first uploaded to the remote machine, then build operation is started and finally, if everything goes fine, binary version of the application is downloaded to the test environment. 

SSH plugin supports SSH and SCP protocols.



To install the plugin please run:

###### Windows

```
unicorn\plugins\ssh\install.cmd
```

###### Linux

```
unicorn/plugins/ssh/install.sh
```



### Recommended plugins

#### webimacs

After installing `webimacs` plugin `config/simdata.cfg` file will be automatically populated using the SIM data from Webimacs DB 





### Required parameters

Following parameters should be set in Unicorn's config  (`config/local.cfg`) to allow proper test execution. Please notice that this kind of configuration is used in the old test concept used in Bobcat project, where ClearCase was used for storing applications and not Artifactory. When Artifactory interfacing is described, additional parameters would be required to be set.





On development or CI environments which are always compiling application from the sources only following parameters must be set: 

```
path_to_aktuell = \\gtoshare\aktuell
ssh_linux_build_server = 10.0.2.213, 22, user, $pass$, config\devconfig\sites\wroclaw\ssh_linux_build_server\rsa
embedded_linux_src_linux_build_server = /home/wrobuildserver.st/linux_src
embedded_linux_src_local = external_repos\linux_src
embedded_linux_default_at_channel = 
embedded_linux_force_build = False

```



`ssh_linux_build_server` - parameters which are used to establish SSH/SCP connection with the Linux build machine. Please notice, that both password and SSH key needs to be entered.

`embedded_linux_src_local` - path to the Git repository where Linux application sources are kept.

For Berlin site this is repo: https://beigitlab.gemalto.com/m2m-testtools/embedded-linux-tools

`embedded_linux_src_linux_build_server` - path on the remote Linux machine where Linux git repo will be uploaded.



On environments which should never build the applications but always use binary form instead:

```
path_to_aktuell = o:\aktuell
```



`path_to_aktuell` - ClearCase path, DSTL function will search for binary version of the application there. For example in:

`o:\aktuell\bobcat\step_01\systemtest\testware_bin\bobcat_100_076a\arc_ril\LinuxArcRilEngine\GTO_cpp\LinuxArcRilEngine`



Test environments which have all parameters set:

```
path_to_aktuell = o:\aktuell
embedded_linux_src_local = C:\linux_src
ssh_linux_build_server = 192.168.56.103, 22, dev, $password$, D:\ssh_keys_dev\id_rsa
embedded_linux_src_linux_build_server = /projects/linux_src
```

will allow both kind of executions:

if binary version of the application is available for the current firmware version it will be used. Otherwise, test environment will connect to the build machine and perform the compilation on-the-fly.



##### Optional parameters

To assume that this is entry point for test execution and leave the module with the specific AT channel configuration:

```
embedded_linux_default_at_channel = 

```

To force compilation even if binary version of the application exists:

```
embedded_linux_force_build = False
```







## Module detection

To allow proper module version and type handling we need to perform detection procedure. In order to do it please import DSTL function:



```
from dstl.auxiliary.init import dstl_detect
```



and then execute it on the DUT device:

```
test.dut.dstl_detect()
```



after successful execution `test.dut` object will have following attributes assigned:

```
test.dut.platform
test.dut.product
test.dut.project
test.dut.step
test.dut.variant
test.dut.software
```





## Precondition functions

This is the function which needs to be run before regular test procedure. It is used to make sure that interfaces are enabled and RIL will run correctly on the module. 

Please import:

```
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions

```

and then use it as follows:

```
    def setup(test):    
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
```




## Postconditions functions

Please import:
```
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
```

Then use:

```
test.dut.dstl_embedded_linux_postconditions()
```

or with explicit AT channel to be set after test:

```
test.dut.dstl_embedded_linux_postconditions('external')
```
If AT channel is not entered as a parameter, it will be reverted to the initial one.



## Building, loading and executing applications

There are only two DSTL functions to handle Linux applications:

`dstl_embedded_linux_prepare_application` - either cross compiles application from the sources and puts binary version of it on the module's filesystem or accesses ClearCase/Artifactory, fetches binary version and puts it on the module.



`dstl_embedded_linux_run_application` - executes Linux application on the module, in Linux userspace



In order to use the functions please import them:

```
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application
```





To prepare the application so it is usable on the module:

```
test.dut.dstl_embedded_linux_prepare_application("arc_ril\\callcontrol\\ecall\\ARC_ECallDial", "/home/cust/demo")
```

```
test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine", "/home/cust/demo")
```



first argument is the path on `linux` git repo where sources of the application are stored,

second argument is path on the module where application should be uploaded.

Function will automatically determine whether it should use binary version of the application (if access to remote binaries repository - ClearCase or Artifactory is available, and application was build in advance) or it should perform the cross compilation by itself by sending the request to Linux build server.

We can also force the build:

```
test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine", "/home/cust/demo", build=True)
```

this option is useful especially during development process.



To execute the application on the module:

```
test.dut.dstl_embedded_linux_run_application("/home/cust/demo/LinuxArcRilEngine procedure=test", "success")
```

This function has two arguments:

- invocation line - this line describes how to execute the application, there is path to the application on the module and optional parameters
- expect message - this value describes what is the expected outcome after executing the application





Example test script



```python
# responsible: 
# location: 
# TC0000001.001 

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\callcontrol\\ecall\\ARC_ECallDial")

    def run(test):
        result,output = test.dut.dstl_embedded_linux_run_application("ARC_ECallDial")
        test.expect('success' in output)
  
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()
        

if "__main__" == __name__:
    unicorn.main()

```



