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
        
        test.ssh_server.send_and_receive(f"pwd")
        path_to_sdk = test.ssh_server.last_response.rstrip()+"/"
        
        
        test.ssh_server.upload(f"{sys.path[0]}/external_repos/linux_src/src/scripts/sdk/LinuxSdkLibrariesDependencyAndPathCheck/LinuxSdkLibrariesDependencyAndPathCheck.sh", f"./LinuxSdkLibrariesDependencyAndPathCheck.sh")
        
        test.ssh_server.send_and_receive(f"chmod +x {path_to_sdk}LinuxSdkLibrariesDependencyAndPathCheck.sh")
        test.expect(test.dut.adb.last_retcode == 0)
        
        test.ssh_server.send_and_verify(f"source /usr/local/oecore-x86_64/environment-setup-cortexa8hf-vfp-neon-oe-linux-gnueabi && {path_to_sdk}LinuxSdkLibrariesDependencyAndPathCheck.sh",f"Every library in /usr/lib is ok.*Every library in /usr/local/oecore-x86_64/sysroots/x86_64-oesdk-linux/usr/lib/ is ok")
        test.expect(test.dut.adb.last_retcode == 0)
        
        
        #test.log.info("Push test application to module tmpfs filesystem:")
        #ret1 = test.dut.adb.push(f"{sys.path[0]}/src/scripts/sdk/LinuxSdkLibrariesDependencyAndPathCheck/LinuxSdkLibrariesDependencyAndPathCheck.sh", "/tmp/LinuxSdkLibrariesDependencyAndPathCheck.sh")
        #test.expect(ret1)
        #test.log.info("Add +x to file:")
        #ret5 = test.dut.adb.send_and_receive(f"chmod +x /tmp/LinuxSdkLibrariesDependencyAndPathCheck.sh")
        #test.expect(test.dut.adb.last_retcode == 0)
        
        # Classic test filesystem
        #test.log.info("Classic test ubifs filesystem")
        #result,output = test.dut.dstl_embedded_linux_run_application("/tmp/LinuxFFSLoadBigDataFS.sh FOLDER_TEST=/home")
        #test.expect('File was successfully deleted' in output)
        
        


        



    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions('external')

if "__main__" == __name__:
    unicorn.main()
    