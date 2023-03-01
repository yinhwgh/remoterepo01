import sys
import os
import unicorn
import shutil
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

dir = "LinuxSdkLibrariesFunctionCheck"

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('external')
        
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -rf {dir}")
        os.mkdir(dir)
 

        

    def run(test):
    
        # query product version with ati
        test.expect(dstl_check_ati1_response(test.dut))
        
        test.ssh_server.send_and_receive(f"pwd")
        path_to_sdk = test.ssh_server.last_response.rstrip()+"/"
        
        
      
        test.dut.adb.pull("/usr/lib", f"./{dir}/libs_adb")
        test.expect(test.dut.adb.last_retcode == 0)
        test.dut.adb.pull("/lib", f"./{dir}/libs_adb")
        test.expect(test.dut.adb.last_retcode == 0)
        shutil.make_archive(f"./{dir}/libs_adb", 'zip', f"./{dir}/libs_adb")
        
        test.ssh_server.send_and_receive(f"mkdir {dir}")
        test.expect(test.ssh_server.last_retcode == 0)
        test.ssh_server.upload(f"{sys.path[0]}/external_repos/linux_src/src/scripts/sdk/LinuxSdkLibs/check_libs.py", f"./{dir}/check_libs.py")
        test.expect(test.ssh_server.last_retcode == 0)
        test.ssh_server.upload(f"./{dir}/libs_adb.zip", f"./{dir}/libs_adb.zip")
        test.expect(test.ssh_server.last_retcode == 0)
        test.ssh_server.send_and_receive(f"cd ./{dir} && unzip libs_adb.zip")
        test.expect(test.ssh_server.last_retcode == 0)
        ssout = test.ssh_server.send_and_receive(f"cd ./{dir} && python check_libs.py --so_deps")
        test.expect(test.ssh_server.last_retcode == 0)
        

      


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions('external')
        test.os.execute(f"rm -rf {dir}")
        test.ssh_server.send_and_receive(f"rm -rf {dir}")

if "__main__" == __name__:
    unicorn.main()
    