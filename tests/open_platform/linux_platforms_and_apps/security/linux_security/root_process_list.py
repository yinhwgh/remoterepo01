# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn
from core.basetest import BaseTest



class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
    
        ALLOWED_ROOT_DAEMONS=[
                'QCMAP_ConnectionManager',
                '/usr/bin/qti',
                '/usr/bin/netmgrd',
                '/usr/bin/adbd',
                '/bin/sh'

        ]

        
        test.log.info("Check list of root daemons in the system")
        
        test.dut.adb.send_and_receive("ps | grep root | awk '{print $5}'")
        test.expect(test.dut.adb.last_retcode == 0)
     

        
        mode_list_ps = list(test.dut.adb.last_response.split("\n"))
        
        
        for i in mode_list_ps:
            print(f"{i}")
            test.expect( search(ALLOWED_ROOT_DAEMONS, i.rstrip() ) )
        


    def cleanup(test):
        pass
        
        
        

def search(list, line):
    for i in range(len(list)):
        if list[i] == line:
            return True
    return False
