import sys
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

from dstl.identification.check_identification_ati import dstl_check_ati1_response


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('external')

        

    def run(test):
    
        # query product version with ati
        test.expect(dstl_check_ati1_response(test.dut))
        
        test.log.info("Push test application to module tmpfs filesystem:")
        ret1 = test.dut.adb.push(f"{sys.path[0]}/external_repos/linux_src/src/scripts/var/LinuxFFSStressFSCreate/LinuxFFSStressFSCreate.sh", "/tmp/LinuxFFSStressFSCreate.sh")
        test.expect(ret1)
        test.log.info("Add +x to file:")
        test.dut.adb.send_and_receive(f"chmod +x /tmp/LinuxFFSStressFSCreate.sh")
        test.expect(test.dut.adb.last_retcode == 0)
        
        # Classic test filesystem
        test.log.info("Classic test ubifs filesystem")
        test.dut.adb.send_and_receive(f"while true; do echo `date`; sleep 60; done & /tmp/LinuxFFSStressFSCreate.sh RepeatTest=2 FolderTest=/home/cust SourceFolder=/home/cust MaxFileSize=0.064")
        test.expect(test.dut.adb.last_retcode == 0)
        
        #result,output = test.dut.dstl_embedded_linux_run_application("/tmp/LinuxFFSLoadBigDataFS.sh FOLDER_TEST=/home")
        #test.expect('File was successfully deleted' in output)
     


        



    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions('external')

if "__main__" == __name__:
    unicorn.main()