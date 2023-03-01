# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn

from core.basetest import BaseTest

dir = "temp_iozone_time_path"





class Test(BaseTest):

    def setup(test):
    
       
        pass

    def run(test):

#---------------------------------------------------------------------------------------        
        test.log.info(f"Push systemd-analyze to /tmp/")
#---------------------------------------------------------------------------------------        
        ret1 = test.dut.adb.push(f"./tests/open_platform/linux_platforms_and_apps/security/packages/iozone", "/tmp/")
        test.expect(ret1)
#---------------------------------------------------------------------------------------    
        test.log.info(f"Check iozone in /tmp")
#--------------------------------------------------------------------------------------- 
        ret2 = test.dut.adb.send_and_verify(f"ls -al /tmp/", ".*iozone.*")
        test.expect(ret2)
#---------------------------------------------------------------------------------------                        
        test.log.info(f"Create 4MB to /tmp/")
#---------------------------------------------------------------------------------------        
        ret1 = test.dut.adb.send_and_verify(f"dd if=/dev/urandom of=/check_file bs=256k count=16", ".*4194304.*")
        test.expect(ret1)
#---------------------------------------------------------------------------------------    
        test.log.info(f"Check created file in /tmp/")
#--------------------------------------------------------------------------------------- 
        ret2 = test.dut.adb.send_and_verify(f"ls -al /", ".*check_file.*")
        test.expect(ret2)
#---------------------------------------------------------------------------------------    
        test.log.info(f"Clear memory caches")
#--------------------------------------------------------------------------------------- 
        test.dut.adb.send_and_receive("sync; echo 3 > /proc/sys/vm/drop_caches")        
        if( test.dut.adb.last_retcode == 0):
            test.expect(True)
        else:
            test.log.error("last_retcode unequal 0")
            test.expect(False)
#---------------------------------------------------------------------------------------    
        test.log.info(f"Check FS performance with iozone")
#--------------------------------------------------------------------------------------- 
        test.dut.adb.send_and_verify("/tmp/iozone -i 1 -+u -+E -f /check_file", ".*iozone.*test.*complete.*")        
        if( test.dut.adb.last_retcode == 0):
            test.expect(True)
        else:
            test.log.error("last_retcode unequal 0")
            test.expect(False)        
#---------------------------------------------------------------------------------------        
        
    def cleanup(test):
        test.dut.adb.send_and_receive("rm /tmp/iozone")
        test.dut.adb.send_and_receive("rm /check_file")
        pass
        
      
 
 
