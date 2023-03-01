#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0105095.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module

class Test(BaseTest):
    """ TC0105095.001 - snsrat_basic_check
    Intention:
        1. test/read/write command
        2. pin locked/unlocked
        3. valid/invalid parameter set
        4. check setting is stored nv
        Description:
        1. Restart module with sim card which pin locked is enabled.
        2. Keep pin is locked.
        3. Check test command AT^SNSRAT=?
        Verify ^SNSRAT: (0,2,7),(0,2,7),(0,2,7) returned
        4. Check write/read command
            AT^SNSRAT=0  OK returned
            AT^SNSRAT?  ^SXRAT:0 returned
            AT^SNSRAT=2  OK returned
            AT^SNSRAT?  ^SXRAT:2 returned
            AT^SNSRAT=7  OK returned
            AT^SNSRAT?  ^SXRAT:7 returned
            AT^SNSRAT=0,2  OK returned
            AT^SNSRAT?  ^SXRAT:0,2 returned
            AT^SNSRAT=2,7  OK returned
            AT^SNSRAT?  ^SXRAT:2,7 returned
            AT^SNSRAT=0,2,7  OK returned
            AT^SNSRAT?  ^SXRAT:0,2,7 returned
            AT^SNSRAT=7,0,2  OK returned
            AT^SNSRAT?  ^SXRAT:7,0,2 returned
        5. Unlock pin and repeat step3-4, result should be expected
        6. Check invalid parameter below, error should be issued
        AT^SNSRAT=3  error returned
        AT^SNSRAT=aa  error returned
        AT^SNSRAT=27, error returned
        7. Restart module check parameters keep the last setting
        AT^SNSRAT?  ^SXRAT:7,0,2 returned
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        rats=['0','2','7']
        test.log.step("1. Restart module with sim card which pin locked is enabled.")
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

        test.log.step("2. Keep pin is locked.")
        test.attempt(test.dut.at1.send_and_verify, "AT+CPIN?", "SIM PIN", retry=3, sleep=1)

        test.log.step("3. Check test command AT^SNSRAT=?, Verify ^SNSRAT: (0,2,7),(0,2,7),(0,2,7) returned")
        expect_test_resp = "\^SNSRAT: \({0}\), \({0}\), \({0}\)".format(','.join(rats))
        test.expect(test.dut.at1.send_and_verify("AT^SNSRAT=?", expect_test_resp))

        test.log.step("4. Check write/read command")
        nv_value = test.check_write_read_commands()

        test.log.step("5. Unlock pin and repeat step3-4, result should be expected")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT^SNSRAT=?", expect_test_resp))
        nv_value = test.check_write_read_commands()

        test.log.step("6. Check invalid parameter below, error should be issued")
        invalid_parameters = ['3', 'aa', '27']
        for invalid_param in invalid_parameters:
            test.expect(test.dut.at1.send_and_verify(f"AT^SNSRAT={invalid_param}", "ERROR"))

        test.log.step("7. Restart module check parameters keep the last setting")
        test.expect(test.dut.dstl_restart())
        nv_value = nv_value.replace(',',',\\s?')
        test.expect(test.dut.at1.send_and_verify("AT^SNSRAT?", f"\^SNSRAT: {nv_value}"))
 

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT^SNSRAT=7,2,0", "OK"))
    
    def check_write_read_commands(test):
        parameters = ['0', '2', '7', '0,2', '2,7', '0,2,7', '7,0,2']
        nv_value = '0'
        for param in parameters:
            updated = test.dut.at1.send_and_verify(f"AT^SNSRAT={param}", "OK")
            test.expect(updated, msg="Fail to set {}".format(f"AT^SNSRAT={param}"))
            expect_value = param.replace(',', ',\\s?')
            test.expect(test.dut.at1.send_and_verify("AT^SNSRAT?", f"\^SNSRAT: {expect_value}"))
            if updated:
                nv_value = param
        return nv_value

if "__main__" == __name__:
    unicorn.main()