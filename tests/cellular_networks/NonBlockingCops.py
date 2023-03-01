#responsible: thomas.troeger@thalesgroup.com
#location: Berlin
#TC0087993.001

import unicorn
from core.basetest import BaseTest

from dstl.internet_service import lwm2m_service
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.auxiliary import check_urc
import random


class Test(BaseTest):
    """ kurz Kommentar
    Non Blocking Cops Pops up


    """

    def __init__(self):
        super().__init__()
        self.dut = None

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        pass

    def run(test):
        imsi = test.dut.sim.imsi
        test.log.com('IMSI' + imsi)

        mcc_mnc: object = imsi[0:5]
        test.log.com('mcc_mnc' + mcc_mnc)

        # enable creg indication with at + creg=2
        test.dut.at1.send_and_verify("at+creg=2", "OK")

        # enable text error message format
        test.dut.at1.send_and_verify("at+cmee=2", "OK")

        # check  AT^SCFG="MEopMode/NonBlock/Cops" ----> must be 0
        test.expect(test.dut.at1.send_and_verify(" AT^SCFG=\"MEopMode/NonBlock/Cops\",\"0\"", '.*SCFG: "MEopMode/NonBlock/Cops","0".*'))
        test.sleep(5)
        # enter pin with at+cpin="PIN1" and wait for registration
        test.dut.dstl_enter_pin()
        test.sleep(15)
        # ry to register to an non existing operater like 26288 with at+cops=1,2,26288
        test.dut.at1.send("at+cops=1,2,28888")
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify(" AT", '.*CME ERROR: no network service.*', timeout=2))
        test.sleep(5)
        # enable non blocking cops feature with with AT^SCFG="MEopMode/NonBlock/Cops,1
        test.expect(test.dut.at1.send_and_verify(" AT^SCFG=\"MEopMode/NonBlock/Cops\",\"1\"", '.*SCFG: "MEopMode/NonBlock/Cops","1".*'))
        test.dut.at1.send_and_verify("at+cops=1,2,27777", "OK", timeout=2)
        test.sleep(10)
        # select manually home operater with at+cops=1,2,"hplmn"
        test.dut.at1.send_and_verify("at+cops=1,2,"+mcc_mnc, "OK", 5)

        # wait for network registration
        test.dut.dstl_check_urc(".*CREG: 1.*", 60)
        test.sleep(5)
        # repair   set cops=0 as default
        test.dut.at1.send_and_verify("at+cops=0", "OK", timeout=5)
        # repair   AT^SCFG="MEopMode/NonBlock/Cops" ----> must be 0 at default
        test.expect(test.dut.at1.send_and_verify(" AT^SCFG=\"MEopMode/NonBlock/Cops\",\"0\"", '.*SCFG: "MEopMode/NonBlock/Cops","0".*'))


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
