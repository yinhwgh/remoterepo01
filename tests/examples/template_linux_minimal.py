# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_linux

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei


from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        """
        In order to use <dstl_embedded_linux_prepare_application> following parameters must be set in local.cfg:

            path_to_aktuell = O:\aktuell # (mandatory)
            ssh_linux_build_server = 10.0.2.213, 22, wrobuildserver.st, <password>, D:\ssh_keys_wrostbuildserver\rsa # (optional)
            embedded_linux_src_local = C:\linux_src # (optional)
            embedded_linux_src_linux_build_server = /home/<user>/linux_src # (optional)

        if binary version is available on the aktuell view it will be used. Otherwise, function will try to build it from sources using dedicated Linux build server (in this case optional build server configuration must be set!)

        """
        dstl_detect(test.dut)
        dstl_embedded_linux_preconditions(test.dut)

    def run(test):
        dstl_embedded_linux_prepare_application(test.dut, "arc_ril\\LinuxArcRilEngine", "/home/cust/demo")
        dstl_embedded_linux_run_application(test.dut, "/home/cust/demo/LinuxArcRilEngine procedure=test", expect="EXP")

    def cleanup(test):
        dstl_embedded_linux_postconditions(test.dut)


if "__main__" == __name__:
    unicorn.main()
