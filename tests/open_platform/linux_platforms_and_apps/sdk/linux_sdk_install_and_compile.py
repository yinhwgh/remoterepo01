import unicorn
import os
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart

from dstl.embedded_system.linux.configuration import dstl_embedded_linux_adb_configuration
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application

dir = "LinuxSdkInstallAndCompile"
path_to_sdk = "/home/wrobuildserver.st/"

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        #test.dut.dstl_embedded_linux_adb_configuration('serial')
        test.dut.dstl_embedded_linux_preconditions('external')
        #test.dut.dstl_embedded_linux_prepare_application("arc_ril\\callcontrol\\ecall\\ARC_ECallDial")
        #test.dut.dstl_embedded_linux_preconditions()
        test.ssh_server.send_and_receive(f'python3 /srv/appbuilder/sdk_setup.py --sw {test.dut.software}')
        test.ssh_server.send_and_verify("ls -la ./sdk", "..")
        test.ssh_server.send_and_receive(f"mkdir {dir}")
        test.ssh_server.send_and_receive(f"pwd")
        path_to_sdk = test.ssh_server.last_response.rstrip()+"/"
        
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -rf {dir}")
       
        os.mkdir(dir)

        
        test.log.info("Add basic build script: copy_sdk.sh")
        sdk_copy(dir,path_to_sdk)
        
        test.log.info("Add basic build script: install_wrapper.sh")
        install_wrapper(dir)
        
        test.log.info("Add basic c file: testcpp.cpp")
        c_example_file(dir)
        
        test.log.info("Add basic build script: basic_c_build.sh")
        c_build_script(dir,path_to_sdk)


        test.ssh_server.upload(f"./{dir}/copy_sdk.sh", f"{path_to_sdk}/{dir}/copy_sdk.sh")
        test.ssh_server.send_and_receive(f"chmod +x {path_to_sdk}/{dir}/copy_sdk.sh")
        test.expect(test.ssh_server.last_retcode == 0)
        test.ssh_server.upload(f"./{dir}/install_wrapper.sh", f"{path_to_sdk}/{dir}/install_wrapper.sh")
        test.ssh_server.send_and_receive(f"chmod +x {path_to_sdk}/{dir}/install_wrapper.sh")
        test.expect(test.ssh_server.last_retcode == 0)
        test.ssh_server.upload(f"./{dir}/testc.c", f"{path_to_sdk}/{dir}/testc.c")
        test.ssh_server.send_and_receive(f"chmod +x {path_to_sdk}/{dir}/testc.c")
        test.expect(test.ssh_server.last_retcode == 0)
        test.ssh_server.upload(f"./{dir}/basic_c_build.sh", f"{path_to_sdk}/{dir}/basic_c_build.sh")
        test.ssh_server.send_and_receive(f"chmod +x {path_to_sdk}/{dir}/basic_c_build.sh")
        test.expect(test.ssh_server.last_retcode == 0)

    def run(test):
    
        # query product version with ati
        res = test.dut.at1.send_and_verify("ati", ".*")
        test.expect(res)
        test.log.info(f"Copy sdk file to: {dir}")
        ret1 =  test.ssh_server.send_and_verify(f"./{dir}/copy_sdk.sh", ".*Success.*")
        test.expect(ret1)
        test.log.info(f"Install sdk to system")
        ret2 = test.ssh_server.send_and_verify(f"./{dir}/install_wrapper.sh", f"{dir}/install/environment-setup-cortexa8hf-vfp-neon-oe-linux-gnueabi.*SDK directory exists as expected.*")
        test.expect(ret2)
        test.log.info(f"Run basic compile process:")
        ret3 = test.ssh_server.send_and_verify(f"./{dir}/basic_c_build.sh", ".*Compile.*Success.*ELF.*32-bit.*ARM.*dynamically.*linked.*")
        test.expect(ret3)
        test.log.info("Get test application from remote build server:")
        test.ssh_server.download(f"{path_to_sdk}/{dir}/testc", f"./{dir}/testc")
        test.log.info("Push test application to module tmpfs filesystem:")
        ret4 = test.dut.adb.push(f"./{dir}/testc", "/tmp/testc")
        test.expect(ret4)
        test.log.info("Add +x to file:")
        ret5 = test.dut.adb.send_and_receive(f"chmod +x /tmp/testc")
        test.expect(test.dut.adb.last_retcode == 0)
        test.log.info("Execute test application on module:")
        ret6 = test.dut.adb.send_and_verify(f"/tmp/testc", "WorksC!")
        test.expect(ret6)




        
        #test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine", "/home/cust/demo")
        
        #test.dut.adb.send_and_receive('python3 /srv/appbuilder/sdk_setup.py --sw BOBCAT_135_002')
        
        #test.expect('..' in test.dut.adb.last_response)
        
        
        #test.ssh_server.send_and_verify("ls -la ./sdk", "install")
        
        #test.ssh_server.send_and_receive(f"find /usr/local -name \"install_sdk.sh\" ")
  
        #print(test.dut.platform)
        #print(test.dut.product)
        #print(test.dut.project)
        #print(test.dut.step)
        #print(test.dut.variant)
        #print(test.dut.software)
        #print(test.dut.software)



        #test.dut.adb.send_and_receive('ps | grep rild')
        #test.expect('gto-rild' in test.dut.adb.last_response)


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions('external')
        test.os.execute(f"rm -rf {dir}")
      
        test.ssh_server.send_and_receive(f"rm -rf {dir}")



def sdk_copy(dir,path):
    x = f"""#!/bin/bash
        sdk_path_tar=$(find {path}/sdk -name "oecore-x86_64-cortexa8hf-vfp-neon-toolchain-ALAS66A-r01.252-a01.000.01.tar.bz2")
        #echo "$sdk_path_tar"
        sdk_path_install=$(find {path}/sdk -name "install_sdk.sh")
        #echo "$sdk_path_install"
        cp -avr $sdk_path_tar `pwd`/{dir} && echo "Success"
        cp -avr $sdk_path_install `pwd`/{dir} && echo "Success"
        chmod +x `pwd`/{dir}/install_sdk.sh && echo "Success"
        
        """
    with open(dir + "/copy_sdk.sh","w+", newline='\n') as f:
         f.writelines(x)
    os.chmod(dir + "/copy_sdk.sh", 509)

def install_wrapper(dir):
    x = f"""#!/bin/bash
        # PLEASE CHECK IF THOSE PATHS ARE FILLED CORRECTLY AFTER EACH SDK CHANGE
        SDK_DIR="install"
        SDK_SRC_ENV="SDK_DIR/environment-setup-cortexa8hf-vfp-neon-oe-linux-gnueabi"
        CURRENT_USER=$(whoami)
        echo "Currently logged user: $CURRENT_USER"

        if [ -d "$SDK_DIR" ]; then
           echo "Removing old SDK"
           rm -rf $SDK_DIR
        fi

        #
        cd `pwd`/{dir}
        ./install_sdk.sh -y -d $SDK_DIR
        cd `pwd`

        if [ -d "$SDK_DIR" ]; then
           echo "SDK directory exists as expected"
        else
           echo "DIF: Expected SDK path $SDK_DIR does not exist!"
        fi
        """
    with open(dir + "/install_wrapper.sh","w+",  newline='\n') as f:
         f.writelines(x)
    os.chmod(dir + "/install_wrapper.sh", 509)
    
def c_example_file(dir):
    x = """
            #include <stdio.h>
            int main(void) {
                printf("WorksC!\\n");
                return 0;
            }
        """
    with open(dir + "/testc.c","w+",  newline='\n') as f:
         f.writelines(x)
         


    
def c_build_script(dir,path):
    x = f"""#!/bin/bash
        source {path}/{dir}/install/environment-setup-cortexa8hf-vfp-neon-oe-linux-gnueabi  && \\
        $CC -v ./{dir}/testc.c -o ./{dir}/testc && echo "Compile Success" 
        echo $CC
        file ./{dir}/testc
        exit 0 
        """
    with open(dir + "/basic_c_build.sh","w+",  newline='\n') as f:
         f.writelines(x)
    os.chmod(dir + "/basic_c_build.sh", 509)

