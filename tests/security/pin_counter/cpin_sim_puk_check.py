#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0010113.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim


class Test(BaseTest):
    """ TC0010113.001 - TpCpinsimPuk  """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(5)

    def run(test):
        simpuk = test.dut.sim.puk1
        simpin = test.dut.sim.pin1
        test.log.info("1.test input wrong PIN code 3 times")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=?","OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*OK.*"))

        if simpuk :
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"6789\"", ".*CME ERROR: incorrect password.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"6789\"", ".*CME ERROR: incorrect password.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"6789\"", ".*CME ERROR: SIM PUK required.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PUK.*"))
            test.log.info("Restore Pin code")
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\",\"{}\"".format(simpuk,simpin), ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*READY.*"))
        else:
            test.log.error('Error, SIM PUK not logged in webimacs')



    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
