# responsible: haofeng.dding@thalesgroup.com
# location: Dalian
# TC0108045.001


import unicorn
import time
from core.basetest import BaseTest
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from tests.rq6 import ebs_alarmdevice_sendalarm_nf


class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        main_process(test)

    def cleanup(test):
        pass


def NF01_goto_EF_C(test):
    test.log.step('***** NF01_goto_EF_B flow start *****')
    test.expect(ebs_alarmdevice_sendalarm_nf.ebs_sendalarm(test, 2, 1))
    test.log.step('***** NF01_goto_EF_B flow end *****')


def NF03_goto_EF_C(test):
    test.log.step('***** NF03_goto_EF_B flow start *****')
    test.expect(ebs_alarmdevice_sendalarm_nf.ebs_sendalarm(test, 2, 3))
    test.log.step('***** NF03_goto_EF_B flow end *****')


def main_process(test):
    ebs_alarmdevice_sendalarm_nf.ebs_check_network(test, 1)
    NF01_goto_EF_C(test)
    NF03_goto_EF_C(test)
    test.expect(test.dut.at1.send_and_verify('AT^SISC=1', ".*OK.*"))
    test.dut.at1.send_and_verify("at+ipr={}".format(115200), "OK", timeout=10)
    test.dut.at1.reconfigure({"baudrate": 115200})
    test.dut.at1.send_and_verify('at^scfg="GPRS/AutoAttach","enabled"', ".*OK.*")


if "__main__" == __name__:
    unicorn.main()
