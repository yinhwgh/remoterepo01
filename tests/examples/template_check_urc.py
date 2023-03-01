# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_check_urc

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei

class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        test.log.step('1. Change CFUN to suspend network service')
        res = test.dut.at1.send_and_verify('at+cfun=5', 'OK')
        test.expect(res, critical=True)

        test.log.step('2. Enter PIN')
        test.dut.dstl_enter_pin()

        test.log.step('3. Enable CREG status reports')
        res = test.dut.at1.send_and_verify('at+creg=2', 'OK')
        test.expect(res)
        res = test.dut.at1.send_and_verify('at+cereg=2', 'OK')
        test.expect(res)
        res = test.dut.at1.send_and_verify('at+cgreg=2', 'OK')
        test.expect(res)

        test.log.step('4. Resume network service by changing CFUN and wait for URC')
        test.dut.at1.send('at+cfun=1')
        test.sleep(5)
        res = test.dut.at1.wait_for("+CREG: 2", timeout=90)
        test.expect(res, critical=True)

        test.log.step('5. Change CFUN again to suspend network service')
        test.dut.at1.send_and_verify('at+cfun=5')
        test.sleep(5)
        test.expect('OK' in test.dut.at1.last_response, critical=True)


        test.log.step('6. Resume network service by changing CFUN')
        res = test.dut.at1.send_and_verify('at+cfun=1', 'OK', append=True)
        test.expect(res, critical=True)

        test.log.step('7. Run network queries with append. Check if URC comes')
        for i in range(10):
            res = test.dut.at1.send_and_verify('at^smoni', 'OK', append=True)
            test.expect(res)
            res = test.dut.at1.send_and_verify('at+csq', '.*', append=True)
            test.expect(res)
            test.sleep(1)

            test.expect("at+cfun=1" in test.dut.at1.last_response)
            test.expect("at^smoni" in test.dut.at1.last_response)
            test.expect("at+csq" in test.dut.at1.last_response)
            if "+CREG: 2" in test.dut.at1.last_response:
                test.log.info("+CREG: 2 was found. We may now continue.")
                break
            if i < 9:
                test.log.info("Running loop iteration: {}".format(i))
                test.expect(True)
            else:
                test.log.error("+CREG: 2 was not received from the module. Aborting test.")
                test.expect(False, critical=True)

        test.log.step('8. Change CFUN once again to suspend network service')
        test.dut.at1.send_and_verify('at+cfun=5', 'OK')
        test.sleep(5)

        test.log.step('9. Resume network service by changing CFUN')
        res = test.dut.at1.send_and_verify('at+cfun=1', 'OK')
        test.expect(res, critical=True)

        test.log.step('10. Check URC - whether it occurred immediately or after wait')
        if "+CREG: 2" in test.dut.at1.last_response:
            test.log.info("+CREG: 2 was immediately found. We may now continue.")
        else:
            res = test.dut.at1.wait_for("+CREG: 2", timeout=90)
            test.expect(res)

        test.sleep(5)
        res = test.dut.at1.send_and_verify('at+cops=?', 'OK', timeout=90)
        test.expect(res)
        test.sleep(5)
        res = test.dut.at1.send_and_verify('at+copn', 'OK', timeout=90)
        test.expect(res)
        test.dut.dstl_restart()

    def cleanup(test):
        pass
if "__main__" == __name__:
    unicorn.main()
