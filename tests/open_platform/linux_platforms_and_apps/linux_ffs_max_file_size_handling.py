import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart

from dstl.embedded_system.linux.configuration import dstl_embedded_linux_adb_configuration
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        #test.dut.dstl_embedded_linux_adb_configuration('serial')
        test.dut.dstl_embedded_linux_preconditions('external')
        test.dut.dstl_embedded_linux_prepare_application("var/LinuxAppFfsMaxFileSizeHandling", "/tmp/LinuxAppFfsMaxFileSizeHandling")
        #test.dut.dstl_embedded_linux_preconditions()

        

    def run(test):
    
        # query product version with ati
        res = test.dut.at1.send_and_verify("ati", ".*")
        
        # Classic /home test filesystem
        result,output = test.dut.dstl_embedded_linux_run_application("/tmp/LinuxAppFfsMaxFileSizeHandling/LinuxAppFfsMaxFileSizeHandling TEST_DIR=/home")
        test.expect('Checksum are the same' in output)
        
        # For /home/cust bobcat step 7 
        if "7" in test.dut.step:
            test.dut.adb.send_and_receive(f'/tmp/LinuxAppFfsMaxFileSizeHandling/LinuxAppFfsMaxFileSizeHandling TEST_DIR=/home/cust')
            test.expect('Checksum are the same' in test.dut.adb.last_response)


        



    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions('external')

if "__main__" == __name__:
    unicorn.main()
