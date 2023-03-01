#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0095389.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import set_sim_waiting_for_pin1


class Test(BaseTest):
    """ TC0095389.001 - SmokeCpin
        Intention :  Simple check of CPIN function
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.sleep(5)

    def run(test):
        simpuk = test.dut.sim.puk1
        simpin = test.dut.sim.pin1
        support_change_by_star_hash = False
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=?","OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"6789\"", ".*CME ERROR: incorrect password.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(simpin), ".*OK.*"))
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.dstl_unlock_sim())
        test.dut.dstl_restart()
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*READY.*OK.*"))
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.dstl_lock_sim())
        test.dut.dstl_restart()
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(simpin), ".*OK.*"))
        test.expect(test.dut.dstl_register_to_network())

        new_pin = "0454"
        #change pin via *#code
        if support_change_by_star_hash:
            test.expect(test.dut.at1.send_and_verify("atd**04*" + simpin + "*"+new_pin+"*"+new_pin+"#", "OK"))
            test.dut.dstl_restart()
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(new_pin), ".*OK.*"))
            test.expect(test.dut.dstl_register_to_network())
            test.expect(test.dut.at1.send_and_verify("at+cpwd=\"SC\",\"{}\",\"{}\"".format(new_pin,simpin), "OK"))
            test.dut.dstl_restart()
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(simpin), ".*OK.*"))

        if simpuk :
            test.dut.dstl_restart()
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
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
