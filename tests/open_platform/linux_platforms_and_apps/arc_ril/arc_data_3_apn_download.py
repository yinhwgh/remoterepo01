# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0104611.001 arc_data_3_apn_download.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilData3ApnDownload")

    def run(test):

        apn_v4 = "internet"
        apn_v6 = "internetipv6"

        try:
            if test.dut.sim.apn_v4: apn_v4 = test.dut.sim.apn_v4
        except KeyError as ex:
            pass
        try:
            if test.dut.sim.apn_v6: apn_v6 = test.dut.sim.apn_v6
        except KeyError as ex:
            pass

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilData3ApnDownload", 
            params=["apn={}".format(apn_v4), "apn2={}".format(format(apn_v6))],
            expect='EXP',
            expect_exit_code=0)

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
