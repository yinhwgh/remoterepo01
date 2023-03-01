#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_basic_broken_symlink_libs_check"

class Test(BaseTest):

    def setup(test):
    
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -rf {dir}")
       
        os.mkdir(dir)
        
        pass

    def run(test):

        """
        Main test scenario is check broken symlink for libs 
        """
        test.log.info(f"Detect broken symlink in path: /lib  (output only: empty)")
        ret1 = test.dut.adb.send_and_verify("find /lib -type l ! -exec test -e {} \; -print; echo empty", "^empty")
        test.expect(test.dut.adb.last_retcode == 0)
        test.expect(ret1)
        
        test.log.info(f"Detect broken symlink in path: /usr/lib   (output only: empty)")
        ret2 = test.dut.adb.send_and_verify("find /usr/lib -type l ! -exec test -e {} \; -print; echo empty", "^empty")
        test.expect(test.dut.adb.last_retcode == 0)
        test.expect(ret2)
        
        
      
        

    def cleanup(test):
        test.os.execute(f"rm -rf {dir}")
        pass

    
