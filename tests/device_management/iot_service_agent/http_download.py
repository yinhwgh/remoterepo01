#responsible: wenyan.wu@thalesgroup.com
#location: Beijing
#TC
import unicorn
from core.basetest import BaseTest

import time

from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):

    def setup(test):
        # test.dut.dstl_restart()
        test.dut.dstl_detect()

    def run(test):
        # test.expect(test.dut.dstl_register_to_network())
        #
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,1'))
        test.expect(test.dut.at1.send_and_verify('at^siss=0,srvType,Http'))
        test.expect(test.dut.at1.send_and_verify('at^siss=0,conId,1'))
        test.expect(test.dut.at1.send_and_verify('at^siss=0,address,"http://www.itte2.com/phpuploader/savefiles/file_3m.zip"'))
        # test.expect(test.dut.at1.send_and_verify('at^siss=0,address,"http://10.163.27.29/index.php"'))

        test.expect(test.dut.at1.send_and_verify('at^siss=0,cmd,get'))
        test.expect(test.dut.at1.send_and_verify('at^siso=0'))
        test.expect(test.dut.at1.wait_for(r"^SISR:"))
        test.expect(test.dut.at1.send_and_verify('at^sisr=0,1000'))
        test.expect(test.dut.at1.send_and_verify('at^srvctl=MODS,start'))

        while True:
            test.expect(test.dut.at1.send_and_verify('at^sisr=0,1000'))
            if r"^SISR: 0,-2" in test.dut.at1.last_response:
                break
            time.sleep(1)

        test.expect(test.dut.at1.send_and_verify('at^sisc=0'))

        # test.thread()

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
