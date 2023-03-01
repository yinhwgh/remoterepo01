#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_sdk_cmake_check"

class Test(BaseTest):

    def setup(test):
    
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -rf {dir}")
       
        os.mkdir(dir)
        
        #test.log.info("Add basic build script: copy_sdk.sh")
        #sdk_copy(dir)
        
        test.log.info("Add basic build script: install_wrapper.sh")
        install_wrapper(dir,test.path_to_sdk)
        pass

    def run(test):

        """
        Main test scenario
        """
        
        test.log.info(f"Compile bash using SDK")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh", "tst"], f".*[100%].*Linking.*CXX.*static.*library.*lib/libtacopie.a.*")
        test.expect(ret1)


        

    def cleanup(test):
        test.os.execute(f"rm -rf {dir}")
        pass

    
def sdk_copy(dir):
    x = f"""#!/bin/bash
    cp -avr /home/tst/kraken_sdk/sudoku-savant-1.3.tar.bz2 `pwd`/{dir} && echo "Success"
    
    """
    with open(dir + "/copy_sdk.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/copy_sdk.sh", 509)

def install_wrapper(dir,path):
    x = f"""#!/bin/bash
        source {path}/sdk/install/environment-setup-aarch64-poky-linux
        cd `pwd`/{dir}
        #git clone https://github.com/Cylix/tacopie.git
        cp ../tests/open_platform/linux_platforms_and_apps/sdk/packages/tacopie.tar.xz ./
        tar -xvf tacopie.tar.xz
        cd tacopie
        cmake --version

        mkdir build
        cd build
        cmake -DCMAKE_INSTALL_PREFIX:PATH=./install ..
        make 
        make install
        file ./install/lib/libtacopie.a
        cd `pwd`

        """
    with open(dir + "/install_wrapper.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/install_wrapper.sh", 509)