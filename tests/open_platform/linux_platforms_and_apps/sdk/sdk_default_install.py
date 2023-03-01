#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_sdk_install"

class Test(BaseTest):

    def setup(test):
    
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -r {dir}")
       
        os.mkdir(dir)
        
        test.log.info("Add basic build script: copy_sdk.sh")
        sdk_copy(dir)
        
        test.log.info("Add basic build script: install_wrapper.sh")
        install_wrapper(dir)
        pass

    def run(test):

        """
        Run simple sdk install command
        """
        
        
        
        
       
        test.log.info(f"Copy sdk file to: {dir}")
        ret1 = test.os.execute_and_verify([f"./{dir}/copy_sdk.sh", "1234"], ".*Success.*")
        test.expect(ret1)
        test.log.info(f"Install sdk to system")
        ret2 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh", "1234"], ".*/usr/local/oecore-x86_64/environment-setup-aarch64-poky-linux.*SDK directory exists as expected.*")
        test.expect(ret2)
      
        

    def cleanup(test):
        test.os.execute(f"rm -r {dir}")
        pass

    
def sdk_copy(dir):
    x = f"""#!/bin/bash
    pwd
    cp -avr ../sdk/*.* `pwd`/{dir} && echo "Success"
    
    """
    with open(dir + "/copy_sdk.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/copy_sdk.sh", 509)

def install_wrapper(dir):
    x = f"""#!/bin/bash
        #==================================================================================================
        # script to install SDK as root on target machine (it is run with sudo)
        # it sends ENTER to the first prompt to use default path and then "y" to proceed with installation
        # author: Tomasz Witka (GL)
        #==================================================================================================

        # PLEASE CHECK IF THOSE PATHS ARE FILLED CORRECTLY AFTER EACH SDK CHANGE
        SDK_DIR="/usr/local/oecore-x86_64"
        SDK_SRC_ENV="SDK_DIR/environment-setup-aarch64-poky-linux"
        SUDO_PASSWD_FILE=$1
        #SUDO_PASSWD=$(cat $SUDO_PASSWD_FILE)
        SUDO_PASSWD=$1
        CURRENT_USER=$(whoami)
        echo "Currently logged user: $CURRENT_USER"

        if [ -d "$SDK_DIR" ]; then
           echo "Removing old SDK"
           sudo -S <<< $SUDO_PASSWD_FILE rm -rf $SDK_DIR
        fi

        #
        cd `pwd`/{dir}
        sudo -S <<< $SUDO_PASSWD_FILE sh -c 'printf "\n y\n" | ./install_sdk.sh'
        cd `pwd`

        if [ -d "$SDK_DIR" ]; then
           echo "SDK directory exists as expected"
        else
           echo "DIF: Expected SDK path $SDK_DIR does not exist!"
        fi
        """
    with open(dir + "/install_wrapper.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/install_wrapper.sh", 509)
