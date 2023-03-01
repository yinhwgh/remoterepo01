#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_sdk_custom_install"

class Test(BaseTest):

    def setup(test):
    
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -rf {dir}")
       
        os.mkdir(dir)
        
        test.log.info("Add basic build script: copy_sdk.sh")
        sdk_copy(dir,test.path_to_sdk)
        
        test.log.info("Add basic build script: install_wrapper.sh")
        install_wrapper(dir)
        pass

    def run(test):

        """
        Main test scenario
        """

        test.log.info(f"Copy sdk file to: {dir}")
        ret1 = test.os.execute_and_verify([f"./{dir}/copy_sdk.sh", "tst"], ".*Success.*")
        test.expect(ret1)
        test.log.info(f"Install sdk to system")
        ret2 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh", "tst"], f"{dir}/install/environment-setup-aarch64-poky-linux.*SDK directory exists as expected.*")
        test.expect(ret2)
      
        

    def cleanup(test):
        test.os.execute(f"rm -rf {dir}")
        pass

    
def sdk_copy(dir,path):
    x = f"""#!/bin/bash
        sdk_path_tar=$(find {path}/sdk -name "oecore-x86_64-aarch64-toolchain-nodistro.0.tar.xz")
        #echo "$sdk_path_tar"
        sdk_path_install=$(find {path}/sdk -name "install_sdk.sh")
        #echo "$sdk_path_install"
        cp -avr $sdk_path_tar `pwd`/{dir} && echo "Success"
        cp -avr $sdk_path_install `pwd`/{dir} && echo "Success"
        
        """
    with open(dir + "/copy_sdk.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/copy_sdk.sh", 509)

def install_wrapper(dir):
    x = f"""#!/bin/bash
        # PLEASE CHECK IF THOSE PATHS ARE FILLED CORRECTLY AFTER EACH SDK CHANGE
        SDK_DIR="install"
        SDK_SRC_ENV="SDK_DIR/environment-setup-aarch64-poky-linux"
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
    with open(dir + "/install_wrapper.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/install_wrapper.sh", 509)