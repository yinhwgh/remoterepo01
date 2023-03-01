#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_sdk_coreutils_install"

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
        
        
        test.log.info(f"Compile coreutils using SDK")
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh", "tst"], f".*ELF.*64-bit.*ARM.*aarch64.*dynamically.*linked.*cp.*(GNU coreutils).*8.32.*.*who.*(GNU coreutils).*8.32.*")
        test.expect(ret1)
        test.log.info(f"Check basic application who and cp on module")
        ret2 = test.dut.adb.push(f"./{dir}/coreutils-8.32/install_coreutils/bin/who", "/tmp/")
        test.expect(ret2)
        ret3 = test.dut.adb.send_and_verify(f"/tmp/who --version", ".*(GNU coreutils).*8.32.*")
        test.expect(ret3)
        ret4 = test.dut.adb.push(f"./{dir}/coreutils-8.32/install_coreutils/bin/cp", "/tmp/")
        test.expect(ret4)
        ret5 = test.dut.adb.send_and_verify(f"/tmp/cp --version", ".*(GNU coreutils).*8.32.*")
        test.expect(ret5)
        

    def cleanup(test):
        test.os.execute(f"rm -rf {dir}")
        test.dut.adb.send_and_receive("rm /tmp/who")
        test.dut.adb.send_and_receive("rm /tmp/cp")
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
        #wget http://ftp.gnu.org/gnu/coreutils/coreutils-8.32.tar.xz
        cp ../tests/open_platform/linux_platforms_and_apps/sdk/packages/coreutils-8.32.tar.xz ./
        tar -xvf coreutils-8.32.tar.xz
        cd coreutils-8.32
        mkdir install_coreutils
        ./configure $CONFIGURE_FLAGS --prefix=`pwd`/install_coreutils
        make 
        make install
        file ./install_coreutils/bin/who
        file ./install_coreutils/bin/cp
        echo "*************************qemu-arm check - cp ****************************************"
        export QEMU_LD_PREFIX={path}/sdk/install/sysroots/aarch64-poky-linux
        qemu-aarch64 ./install_coreutils/bin/cp --version
        echo "*************************qemu-arm check - who ***************************************"
        qemu-aarch64 ./install_coreutils/bin/who --version
        echo "*************************qemu-arm end ***********************************************"
        cd `pwd`
        """
    with open(dir + "/install_wrapper.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/install_wrapper.sh", 509)