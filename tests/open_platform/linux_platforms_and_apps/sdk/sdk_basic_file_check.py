#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_sdk_basic_file_check"

class Test(BaseTest):

    def setup(test):
    
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -rf {dir}")
       
        os.mkdir(dir)
        
        test.log.info("Add basic build script: copy_sdk.sh")
        sdk_copy(dir,test.path_to_sdk)
        
        test.log.info("Add basic build script: check_wrapper.sh")
        check_wrapper(dir)
        pass

    def run(test):

        """
        Main test scenario
        """
        test.log.info(f"Copy sdk file to: {dir}")
        ret1 = test.os.execute_and_verify([f"./{dir}/copy_sdk.sh", "tst"], ".*Success.*")
        test.expect(ret1)
        test.log.info(f"Check SDK files")
        ret2 = test.os.execute_and_verify([f"./{dir}/check_wrapper.sh"], f".*install_sdk.sh.*oecore-x86_64-aarch64-toolchain-nodistro.0.tar.xz.*")
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

def check_wrapper(dir):
    x = f"""#!/bin/bash
        SDK_INSTALL_FILE_NAME="install_sdk.sh"
        SDK_INSTALL_TAR_NAME="oecore-x86_64-aarch64-toolchain-nodistro.0.tar.xz"
        cd `pwd`/{dir}
        ls -al | grep $SDK_INSTALL_FILE_NAME 
        ls -al | grep $SDK_INSTALL_TAR_NAME
        cd `pwd`
        """
    with open(dir + "/check_wrapper.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/check_wrapper.sh", 509)