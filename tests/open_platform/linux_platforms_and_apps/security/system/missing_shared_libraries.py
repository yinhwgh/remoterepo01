# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn

from core.basetest import BaseTest

dir = "temp_missing_shared_libraries_path"





class Test(BaseTest):

    def setup(test):
    
       
        pass

    def run(test):


#---------------------------------------------------------------------------------------        
        test.log.info(f"Check if there are no missing shared libraries") 
#---------------------------------------------------------------------------------------        
        test.log.info(f"Push ldd to /tmp/")
#---------------------------------------------------------------------------------------        
        ret1 = test.dut.adb.push(f"./tests/open_platform/linux_platforms_and_apps/security/packages/ldd", "/tmp/")
        test.expect(ret1)
#---------------------------------------------------------------------------------------    
        test.log.info(f"Check ldd in /tmp")
#--------------------------------------------------------------------------------------- 
        ret2 = test.dut.adb.send_and_verify(f"ls -al /tmp/", ".*ldd.*")
        test.expect(ret2)
#---------------------------------------------------------------------------------------
        test.log.info(f"Check /bin directory")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive("/tmp/ldd /bin/* | grep \"=> not found\"")        
        if( test.dut.adb.last_retcode == 1):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 1")
                test.expect(False)         
#---------------------------------------------------------------------------------------
        test.log.info(f"Check /usr/bin directory")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive("/tmp/ldd /usr/bin/* | grep \"=> not found\"")        
        if( test.dut.adb.last_retcode == 1):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 1")
                test.expect(False)   
#---------------------------------------------------------------------------------------
        test.log.info(f"Check /sbin directory")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive("/tmp/ldd /sbin/* | grep \"=> not found\"")        
        if( test.dut.adb.last_retcode == 1):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 1")
                test.expect(False)  
#---------------------------------------------------------------------------------------
        test.log.info(f"Check /usr/sbin directory")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive("/tmp/ldd /usr/sbin/* | grep \"=> not found\"")        
        if( test.dut.adb.last_retcode == 1):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 1")
                test.expect(False)  
#---------------------------------------------------------------------------------------
        test.log.info(f"Check /lib directory")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive("/tmp/ldd /lib/* | grep \"=> not found\"")        
        if( test.dut.adb.last_retcode == 1):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 1")
                test.expect(False)
#---------------------------------------------------------------------------------------
        test.log.info(f"Check /usr/lib directory")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive("/tmp/ldd /usr/lib/* | grep \"=> not found\"")        
        if( test.dut.adb.last_retcode == 1):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 1")
                test.expect(False)
#---------------------------------------------------------------------------------------
        test.log.info(f"Check /lib64 directory")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive("/tmp/ldd /lib64/* | grep \"=> not found\"")        
        if( test.dut.adb.last_retcode == 1):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 1")
                test.expect(False)
#---------------------------------------------------------------------------------------
        test.log.info(f"Check /usr/lib64 directory")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive("/tmp/ldd /usr/lib64/* | grep \"=> not found\"")        
        if( test.dut.adb.last_retcode == 1):
                test.expect(True)
        else:
                test.log.error("last_retcode unequal 1")
                test.expect(False)
#--------------------------------------------------------------------------------------- 

    def cleanup(test):
        test.dut.adb.send_and_receive("rm /tmp/ldd")

        pass
        
      
 
 
 
 
