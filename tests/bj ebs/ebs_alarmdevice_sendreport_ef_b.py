# responsible: haofeng.dding@thalesgroup.com
# location: Dalian
# TC0108050.001


import unicorn
import time
from core.basetest import BaseTest
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from tests.rq6 import ebs_alarmdevice_sendreport_nf


class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        main_process(test)

    def cleanup(test):
        # test.dut.at1.send_and_verify("at+ipr={}".format(115200), "OK", timeout=10)
        # test.dut.at1.reconfigure({"baudrate": 115200})
        pass


def NF01_goto_EF_B(test):
    test.log.step('***** NF01_goto_EF_B flow start *****')
    test.expect(ebs_alarmdevice_sendreport_nf.ebs_sendreport(test, 1, 1))
    test.log.step('***** NF01_goto_EF_B flow end *****')


def NF02_goto_EF_B(test):
    test.log.step('***** NF02_goto_EF_B flow start *****')
    test.expect(ebs_alarmdevice_sendreport_nf.ebs_sendreport(test, 1, 2))
    test.log.step('***** NF02_goto_EF_B flow end *****')


def NF03_goto_EF_B(test):
    test.log.step('***** NF03_goto_EF_B flow start *****')
    test.expect(ebs_alarmdevice_sendreport_nf.ebs_sendreport(test, 1, 3))
    test.log.step('***** NF03_goto_EF_B flow end *****')


def main_process(test):
    # ebs_alarmdevice_checknetwork_nf(test)
    ebs_alarmdevice_sendreport_nf.ebs_check_network(test, 1)
    NF01_goto_EF_B(test)
    NF02_goto_EF_B(test)
    NF03_goto_EF_B(test)
    test.expect(test.dut.at1.send_and_verify('AT^SISC=1', ".*OK.*"))
    test.dut.at1.send_and_verify("at+ipr={}".format(115200), "OK", timeout=10)
    test.dut.at1.reconfigure({"baudrate": 115200})
    test.dut.at1.send_and_verify('at^scfg="GPRS/AutoAttach","enabled"', ".*OK.*")


if "__main__" == __name__:
    unicorn.main()
