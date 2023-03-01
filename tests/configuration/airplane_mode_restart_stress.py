
# responsible: dan.liu@thalesgroup.com
# location: Dalian
# TC0103618.001

import unicorn
from core.basetest import BaseTest
from core.interface import GenericInterface
from dstl.auxiliary import restart_module
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.configuration import functionality_modes



class AirplaneModeRestartStress(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at+cfun=1', '.*OK.*'))
        test.expect(test.dut.dstl_lock_sim())


    def run(test):


        test.expect(test.dut.at1.send_and_verify('at+cfun?', "\s+OK\s+"))

        run_time = 1

        while run_time < 100:



            test.expect(test.dut.at1.send_and_verify(' AT^SCFG= "MEopMode/CFUN",0', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at+cfun=0','.*OK.*'))

            test.expect(test.dut.at1.send_and_verify('at+cfun=1,1', wait_for="\s+\^SYSSTART AIRPLANE MODE\s+"))

            test.expect(test.dut.at1.send_and_verify('at+cfun?', '.*0.*'))

            test.expect(test.dut.at1.send_and_verify('AT+CPIN?', '.*SIM not inserted.*'))

            test.expect(test.dut.at1.send_and_verify('at+cops=0', '.*ERROR.*'))

            run_time = run_time+1

        else:

            test.expect(test.dut.at1.send_and_verify('at+cfun=1', '.*OK.*'))
            test.sleep(1)
            test.expect(test.dut.at1.send_and_verify('at+cfun=4', '.*OK.*'))

            test.expect(test.dut.at1.send_and_verify('at+cfun=1,1', wait_for="\s+\^SYSSTART AIRPLANE MODE\s+"))

            test.expect(test.dut.at1.send_and_verify('at+cfun?', '.*4.*'))

            test.expect(test.dut.dstl_enter_pin())
            test.expect(test.dut.at1.send_and_verify('at+cops=0', '.*operation not supported.*'))

            run_time = run_time+1

            if run_time == 200:
                pass

    def cleanup(test):

        test.dut.at1.send_and_verify('at+cfun=1','.*OK.*')


if "__main__" == __name__:
    unicorn.main()



















