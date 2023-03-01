# author: hui.yu@thalesgroup.com
# location: Dalian
# LM0001294.001 - LM0001334.001 - LM0003237.001 - LM0003237.002 - LM0003237.011 - LM0003237.012 -
# LM0003237.013 - LM0007549.001 - TC0091675.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.call.setup_voice_call import dstl_voice_call_by_number
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module

testcase_id = "LM0001294.001 - LM0001334.001 - LM0003237.001 - LM0003237.002 - LM0003237.011 - LM0003237.012 - " \
              "LM0003237.013 - LM0007549.001 - TC0091675.001"


class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com("***** " + testcase_id + " *****")
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_get_imei()
        test.r2.dstl_detect()
        test.r2.dstl_get_imei()
        # test.dut.devboard.send_and_verify("mc:asc0cfg=off", ".*O.*")    # switches ASC0 off - do not do this!
        pass

    def run(test):
        test.log.step('Step 1.0: read write command without PIN')
        # ==============================================================

        test.log.step('Step 1.1: check is restart is needed?')
        test.dut.at1.send_and_verify("at+CPIN?", ".*O.*")
        if "READY" in test.dut.at1.last_response:
            test.log.info("restart needed, PIN was enter before")
            test.expect(test.dut.dstl_restart())
        # SIM PIN must be active
        test.dut.at1.send_and_verify("AT+CPIN?", "OK")
        res = test.dut.at1.last_response
        if "READY" in res:
            # check if SIM PIN is active
            test.dut.dstl_lock_sim()
        else:
            test.log.info("SIM PIN is active")

        test.log.step('Step 1.2: check command without PIN')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify('atx0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('atx1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('atx2', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('atx3', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('atx4', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('atx5', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('atx255', 'ERROR'))

        test.log.step('Step 2.0: read write command with PIN')
        # ==============================================================
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at&f', expect='OK'))

        test.log.step('Step 2.1: check if Atx(0-4) can be set')
        # ==============================================================
        for n in range(5):
            test.expect(test.dut.at1.send_and_verify('atX'+str(n), expect='OK'))
            test.expect(test.dut.at1.send_and_verify('at&v', expect='OK'))
            check_string = " X" + str(n) + " "
            if check_string in test.dut.at1.last_response:
                test.expect(True)
                test.log.info("correct value X" + str(n) + " can be set")
            else:
                test.expect(False)
                test.log.info("Wrong value X" + str(n) + " can't be set")

        test.log.step('Step 2.1: check wrong values')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify('at&f', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('atX5', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at&v', expect='OK'))
        if " X0 " in test.dut.at1.last_response:
            test.expect(True)
            test.log.info("correct vaule 5 can't be set")
        else:
            test.expect(False)
            test.log.info("Wrong default vaule after wrong atx5 value")
        test.expect(test.dut.at1.send_and_verify('atX255', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at&v', expect='OK'))
        if " X0 " in test.dut.at1.last_response:
            test.expect(True)
            test.log.info("correct vaule 255 can't be set")
        else:
            test.expect(False)
            test.log.info("Wrong default vaule after wrong atx255 value")

        test.log.step('Step 3.0: Function Test')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify('atx0', expect='OK'))
        test.r1.dstl_register_to_network()
        test.r2.dstl_register_to_network()

        test.log.step('Step 3.1: setup call from remote 1 to remote 2')
        # ==============================================================
        test.log.step('Step 3.2: Deactivate call waiting for 2nd party')
        test.expect(test.r1.at1.send_and_verify('atd#43*#;', '.*CCWA: 0,(1|255).*OK'))
        # test.r1.at1.send_and_verify('at+ccwa=0,0', '.*CCWA: 0,(1|255).*OK')
        test.expect(test.r1.dstl_voice_call_by_number(test.r2, test.r2.sim.nat_voice_nr))
        test.expect(test.r1.at1.send_and_verify('at+CLCC'))
        test.expect(test.r2.at1.send_and_verify('at+CLCC'))

        test.log.step('Step 3.3: check the resonse code for all possible X Values')
        # ==============================================================
        for n in range(5):
            test.log.h3("\n step 3.3 - check response code with atx" + str(n))
            test.expect(test.dut.at1.send_and_verify('atX'+str(n), expect='OK'))
            test.expect(test.dut.at1.send_and_verify('at&v', expect='OK'))
            test.expect(test.dut.at1.send_and_verify('atd' + test.r1.sim.nat_voice_nr + ";", '.*O.*'))
            if n == 3 or n == 4:
                ret = test.expect(test.dut.at1.verify_or_wait_for("BUSY", timeout=30))
                if not ret:
                    test.dut.at1.send_and_verify('at+CLCC')
                    test.dut.at1.send_and_verify('at+CEER')
            else:
                test.expect(test.dut.at1.verify_or_wait_for("NO CARRIER", timeout=55))
            test.sleep(2)
            test.dut.at1.send_and_verify('at+chup')
            test.dut.at1.send_and_verify('at^sblk')

        test.expect(test.dut.at1.send_and_verify('at+chup', '.*O.*'))
        test.expect(test.r1.at1.send_and_verify('at+chup', '.*O.*'))
        test.expect(test.r2.at1.send_and_verify('at+chup', '.*O.*'))

        test.log.step('Step 3.4: activate call waiting for 2nd party')
        test.r1.at1.send_and_verify('atd*43*#;', '.*CCWA: 0,(1|255).*OK')
        pass

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('at+chup', '.*O.*'))
        test.expect(test.r1.at1.send_and_verify('at+chup', '.*O.*'))
        test.expect(test.r2.at1.send_and_verify('at+chup', '.*O.*'))
        test.expect(test.r1.at1.send_and_verify('atd#43*#;', '.*CCWA: 0,(1|255).*OK'))

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass


if '__main__' == __name__:
    unicorn.main()
