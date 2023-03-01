# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn

from core.basetest import BaseTest

dir = "temp_su_path"





class Test(BaseTest):

    def setup(test):
    
       
        pass

    def run(test):

#---------------------------------------------------------------------------------------        
        test.log.info(f"Check su application")
#---------------------------------------------------------------------------------------        
        test.dut.adb.send_and_receive(f"which su")
        if( test.dut.adb.last_retcode == 0):
            test.expect(True)
        else:
            test.log.error("last_retcode unequal 0")
            test.expect(False)
#---------------------------------------------------------------------------------------    


    def cleanup(test):
        

        pass
        
      
 
        
      