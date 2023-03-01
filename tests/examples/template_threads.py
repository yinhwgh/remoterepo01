# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_threads

import unicorn
from core.basetest import BaseTest

from dstl.template import dstl_dummy
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei

class Test(BaseTest):

    def setup(test):
        pass

    def run(test):

        """Starting multiple threads and waiting until they synchronizes with <join>
        """

        for i in range(10):
            t1 = test.thread(test.dut.at1.send_and_verify, "at", expect="OK")
            t2 = test.thread(test.dut.at2.send_and_verify, "at", expect="OK")
            t1.join()
            t2.join()

        t3 = test.thread(test.dut.at1.send_and_verify, "ati")
        t3.name = "X"
        t4 = test.thread(test.dut.at2.send_and_verify, "ati")
        t4.name = "Y"
        t3.join()
        t4.join()

        t5 = test.thread(test.dut.detect)
        t6 = test.thread(test.r1.detect)
        t5.join()
        t6.join()

        t7 = test.thread(test.os.execute, "ping google.com")
        t8 = test.thread(test.dut.at1.send_and_verify, "at")

        t7.join()
        t8.join()

    def cleanup(test):
        pass
