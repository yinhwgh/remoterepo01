#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_sdk_libs_check"

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
        test.log.info(f"Check libs headers")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*ARC_RIL.h.*")
        test.expect(ret1)
        test.log.info(f"Check libs dynamic")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*ArcRil.*so")
        test.expect(ret1)
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*file.*format.*elf64-littleaarch64.*")
        test.expect(ret1)
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh"], f".*Elf.*file.*type.*is.*DYN.*(Shared object file).*")
        test.expect(ret1)
           

    def cleanup(test):
        test.os.execute(f"rm -rf {dir}")
        pass

    


def install_wrapper(dir,path):
    x = f"""#!/bin/bash
            source {path}/sdk/install/environment-setup-aarch64-poky-linux
            find {path}/sdk/install -name "ARC_RIL.h"
            find {path}/sdk/install -name "*ArcRil*.so"
            $OBJDUMP -p `find {path}/sdk/install -name "*ArcRil*.so"`
            readelf -l `find {path}/sdk/install -name "*ArcRil*.so"`
        """
    with open(dir + "/install_wrapper.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/install_wrapper.sh", 509)