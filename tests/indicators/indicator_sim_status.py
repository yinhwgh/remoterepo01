#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0065648.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.auxiliary.devboard import devboard
from dstl.status_control import extended_indicator_control
from dstl.configuration import network_registration_status

class Test(BaseTest):
    """
    TC0065648.001 - IndSimstatus
    Check the status for indicator simstatus in following situations:
    - removed SIM card from the DSB
    - inserted SIM card in the DSB
    - add the pin
    """

    def setup(test):
        test.dut.dstl_detect()
        support_sind_sim_status = test.dut.at1.send_and_verify("AT^SIND?", "\^SIND: simstatus")
        if not support_sind_sim_status:
            test.expect(False, msg=f"Product {test.dut.product} does not support AT^SIND=\"simstatus\", scripts exit")
            exit
        # Set module with pin locked
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_lock_sim())

    def run(test):
        test.log.info("1. Check simstatus of locked SIM")
        test.log.info("1.1 Remove and insert sim card")
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1",".*OK.*"))
        test.sleep(2)
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0",".*OK.*"))
        test.log.info("1.2 Enable indicator of sim status, and check current indicator status is 3: USIM PIN required - USIM locked")
        test.expect(test.dut.dstl_enable_one_indicator("simstatus", check_result=False))
        last_response = test.dut.at1.last_response
        test.expect("^SIND: simstatus,1,1" in last_response, msg="SIM status should be 1 just after sim card is inserted")
        test.sleep(5)
        test.expect(test.dut.dstl_enable_one_indicator("simstatus", check_result=True, indicator_value=3))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,5", timeout=20))
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=1, indicator_value=5))

        test.log.info("2. check simstatus of locked SIM after restart with at^cfun=1,1")
        test.expect(test.dut.dstl_restart())
        test.log.info("2.1 Enable indicator of sim status, and check current indicator status is 3: USIM PIN required - USIM locked")
        test.expect(test.dut.dstl_enable_one_indicator("simstatus", check_result=True, indicator_value=3))
        test.log.info("2.2 Enter pin, and check current indicator status is 5: USIM initialization completed")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,5", timeout=20))
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=1, indicator_value=5))
        test.log.info("2.3 Remove sim card, sim status is 0: USIM removed")
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1",".*OK.*"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,0", timeout=5))
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=1, indicator_value=0))
        test.log.info("2.4 Insert sim card, sim status is 1: USIM inserted, then sim status changes to 3: USIM PIN required - USIM locked")
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0",".*OK.*"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,1", timeout=5))
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,3", timeout=5))
        test.log.info("2.5 Enable CREG URC, enter pin, both simstatus and CREG URC appears")
        test.expect(test.dut.dstl_set_network_registration_urc(domain="CS", urc_mode="1"))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,5", timeout=20))
        test.expect(test.dut.dstl_check_network_registration_urc(domain="CS", expected_state="1"))
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=1, indicator_value=5))

        test.log.info("3. Check simstatus of unlocked SIM")
        test.expect(test.dut.dstl_unlock_sim())
        test.log.info("3.1 Remove and insert sim card")
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1",".*OK.*"))
        test.sleep(2)
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0",".*OK.*"))
        test.log.info("3.2 Sim status URC appear")
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,5", timeout=20, append=True))
        last_response = test.dut.at1.last_response
        test.expect("+CIEV: simstatus,1" in last_response)
        test.expect("+CIEV: simstatus,4" in last_response)
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=1, indicator_value=5))

        test.log.info("4. check simstatus of unlocked SIM after restart with at^cfun=1,1")
        test.expect(test.dut.dstl_restart())
        test.log.info("4.1 Enable indicator of sim status, and check current indicator status is 5: USIM initialization completed")
        test.expect(test.dut.dstl_enable_one_indicator("simstatus"))
        last_response = test.dut.at1.last_response
        test.expect("^SIND: simstatus,1,5" in last_response, msg="sim status value should be 5")
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=1, indicator_value=5))
        test.log.info("4.2 Remove sim card, and check current indicator status is 0: USIM initialization completed")
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1",".*OK.*"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,0", timeout=5))
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=1, indicator_value=0))
        test.log.info("4.3 Insert sim, sim status URC appear")
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0",".*OK.*"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,5", timeout=20, append=True))
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=1, indicator_value=5))
        test.log.info("4.4 Lock pin, remove and insert sim card, sim status is 3: USIM PIN required - USIM locked")
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1",".*OK.*"))
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0",".*OK.*"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,1", timeout=5))
        test.expect(test.dut.at1.wait_for("\+CIEV: simstatus,3", timeout=5))
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=1, indicator_value=3))
        test.log.info("4.5 Disable sim status indicator, sim status mode is 0 and value is 3: USIM PIN required - USIM locked")
        test.expect(test.dut.dstl_disable_one_indicator("simstatus", check_result=True, indicator_value=3))

        test.log.info("5. Sim status URC won't appear with indicator disabled")
        test.expect(test.dut.dstl_restart()) 
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1",".*OK.*"))
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0",".*OK.*"))
        test.expect(not test.dut.at1.wait_for("\+CIEV: simstatus",timeout=5))
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=0, indicator_value=3))
        last_response = test.dut.at1.last_response
        test.expect("\+CIEV: simstatus" not in last_response)
        test.expect(test.dut.dstl_enter_pin())
        test.expect(not test.dut.at1.wait_for("\+CIEV: simstatus", timeout=20))
        test.expect(test.dut.dstl_check_indicator_value("simstatus", mode=0, indicator_value=5))

    def cleanup(test):
        test.expect(test.dut.dstl_insert_sim())
        test.expect(test.dut.dstl_lock_sim())

if "__main__" == __name__:
    unicorn.main()
