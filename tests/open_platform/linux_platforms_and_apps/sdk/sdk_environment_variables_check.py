#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_sdk_environment_variables_check"

class Test(BaseTest):

    def setup(test):
    
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -rf {dir}")
       
        os.mkdir(dir)
        
        
        test.log.info("Add basic build script: install_wrapper.sh")
        install_wrapper(dir,test.path_to_sdk)
        pass

    def run(test):

        """
        Main test scenario
        """
        
        
        
        
       

        test.log.info(f"Check $CC")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-gcc.*")
        test.expect(ret1)
        test.log.info(f"Check $CXX")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-g.*")
        test.expect(ret1)
        test.log.info(f"Check $CPP")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-gcc.*")
        test.expect(ret1)
        test.log.info(f"Check $AS")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-as.*")
        test.expect(ret1)
        test.log.info(f"Check $LD")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-ld.*")
        test.expect(ret1)
        test.log.info(f"Check $GDB")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-gdb.*")
        test.expect(ret1)
        test.log.info(f"Check $STRIP")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-strip.*")
        test.expect(ret1)
        test.log.info(f"Check $RANLIB")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-ranlib.*")
        test.expect(ret1)
        test.log.info(f"Check $OBJCOPY")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-objcopy.*")
        test.expect(ret1)
        test.log.info(f"Check $OBJDUMP ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-objdump.*")
        test.expect(ret1)
        test.log.info(f"Check $AR ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-ar.*")
        test.expect(ret1)
        test.log.info(f"Check $NM ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-nm.*")
        test.expect(ret1)
        test.log.info(f"Check $M4 ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*m4.*")
        test.expect(ret1)
        test.log.info(f"Check $TARGET_PREFIX ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-.*")
        test.expect(ret1)
        test.log.info(f"Check $CROSS_COMPILE ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*aarch64-poky-linux-.*")
        test.expect(ret1)
        test.log.info(f"Check $CONFIGURE_FLAGS ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*--target=aarch64-poky-linux.*")
        test.expect(ret1)
        test.log.info(f"Check $CFLAGS ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*-O2.*")
        test.expect(ret1)
        test.log.info(f"Check $CXXFLAGS ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*-O2.*")
        test.expect(ret1)
        test.log.info(f"Check $LDFLAGS ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*.*")
        test.expect(ret1)
        test.log.info(f"Check $CPPFLAGS ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*.*")
        test.expect(ret1)
        test.log.info(f"Check $ARCH ")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*arm64.*")
        test.expect(ret1)
      
        

    def cleanup(test):
        test.os.execute(f"rm -rf {dir}")
        pass

    


def install_wrapper(dir,path):
    x = f"""#!/bin/bash
            # PLEASE CHECK IF THOSE PATHS ARE FILLED CORRECTLY AFTER EACH SDK CHANGE

            source {path}/sdk/install/environment-setup-aarch64-poky-linux

            echo $CC
            echo $CXX
            echo $CPP
            echo $AS
            echo $LD
            echo $GDB
            echo $STRIP 
            echo $RANLIB 
            echo $OBJCOPY 
            echo $OBJDUMP 
            echo $AR 
            echo $NM 
            echo $M4
            echo $TARGET_PREFIX 
            echo $CROSS_COMPILE 
            echo $CONFIGURE_FLAGS 
            echo $CFLAGS 
            echo $CXXFLAGS 
            echo $LDFLAGS 
            echo $CPPFLAGS 
            echo $ARCH

        """
    with open(dir + "/install_wrapper.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/install_wrapper.sh", 509)