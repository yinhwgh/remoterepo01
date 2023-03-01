#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_sdk_gawk_install"

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
        ret1 = test.os.execute_and_verify([f"./{dir}/install_wrapper.sh", "tst"], f".*ELF.*64-bit.*LSB.*executable.*aarch64.*version.*dynamically.*linked.*")
        test.expect(ret1)
        #ret2 = test.dut.adb.push(f"./{dir}/gawk-5.1.0/install_gawk/bin/gawk", "/home/root/")
        #test.expect(ret2)
        #ret3 = test.dut.adb.send_and_verify(f"/home/root/gawk --version", ".*GNU.*Awk.*5.1.0,.*API:.*3.0.*")
        #test.expect(ret3)
        test.log.info("Push test application to module tmpfs filesystem:")
        ret4 = test.dut.adb.push(f"./{dir}/gawk-5.1.0/install_gawk/bin/gawk", "/tmp/")
        test.expect(ret4)
        test.log.info("Add +x to file:")
        ret5 = test.dut.adb.send_and_receive(f"chmod +x /tmp/gawk")
        test.expect(test.dut.adb.last_retcode == 0)
        test.log.info("Execute test application on module:")
        ret6 = test.dut.adb.send_and_verify(f"/tmp/gawk --version", ".*GNU.*Awk.*5.1.0,.*API:.*3.0.*")
        test.expect(ret6)

        

    def cleanup(test):
        test.os.execute(f"rm -rf {dir}")
        test.dut.adb.send_and_receive("rm /tmp/gawk")
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
        pwd
        #wget http://ftp.gnu.org/gnu/gawk/gawk-5.1.0.tar.xz
        cp ../tests/open_platform/linux_platforms_and_apps/sdk/packages/gawk-5.1.0.tar.xz ./
        tar -xvf gawk-5.1.0.tar.xz
        cd gawk-5.1.0
        mkdir install_gawk
        ./configure $CONFIGURE_FLAGS --prefix=`pwd`/install_gawk
        make 
        make install
        file ./install_gawk/bin/gawk
        echo "*************************qemu-arm check ****************************************"
        export QEMU_LD_PREFIX={path}/sdk/install/sysroots/aarch64-poky-linux
        qemu-aarch64 ./install_gawk/bin/gawk --version
        echo "*************************qemu-arm end ****************************************"
        cd `pwd`

        """
    with open(dir + "/install_wrapper.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/install_wrapper.sh", 509)