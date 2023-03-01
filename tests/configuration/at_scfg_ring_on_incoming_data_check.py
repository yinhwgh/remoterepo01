#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0010424.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module

class Test(BaseTest):
    """
    TC0010424.001 - ScfgRingOnIncomingData
    """

    def setup(test):
        test.log.step('1.Initialization')
        test.dut.dstl_detect()

    def run(test):
        test.log.step('2.Reset module and check "GPRS/RingOnIncomingData" for both interfaces')
        test.dut.dstl_restart()
        test.expect(test.check_status('off',test.dut.at1))
        test.expect(test.check_status('off', test.dut.at2))

        test.log.step('3.Activate "GPRS/RingOnIncomingData" ("on") on first interface.'
                      ' Check values for both interfaces')
        test.expect(test.set_status('on', test.dut.at1))
        test.expect(test.check_status('on', test.dut.at1))
        test.expect(test.check_status('off', test.dut.at2))

        test.log.step('4.Execute AT&F on first interface. Check values for both interfaces')
        test.expect(test.dut.at1.send_and_verify('at&f', 'OK'))
        test.expect(test.check_status('on', test.dut.at1))
        test.expect(test.check_status('off', test.dut.at2))

        test.log.step('5.Activate "GPRS/RingOnIncomingData" ("on") on second interface. '
                      'Check values for both interfaces')
        test.expect(test.set_status('on', test.dut.at2))
        test.expect(test.check_status('on', test.dut.at1))
        test.expect(test.check_status('on', test.dut.at2))

        test.log.step('6.Execute AT&F on first interface. Check values for both interfaces')
        test.expect(test.dut.at1.send_and_verify('at&f', 'OK'))
        test.expect(test.check_status('on', test.dut.at1))
        test.expect(test.check_status('on', test.dut.at2))

        test.log.step('7. Deactivate "GPRS/RingOnIncomingData" ("off") on first interface. '
                      'Check values for both interfaces')
        test.expect(test.set_status('off', test.dut.at1))
        test.expect(test.check_status('off', test.dut.at1))
        test.expect(test.check_status('on', test.dut.at2))

        test.log.step('8. Execute AT&F on first interface. Check values for both interfaces')
        test.expect(test.dut.at1.send_and_verify('at&f', 'OK'))
        test.expect(test.check_status('off', test.dut.at1))
        test.expect(test.check_status('on', test.dut.at2))

        test.log.step('9. Reset module and check "GPRS/RingOnIncomingData" for both interfaces')
        test.dut.dstl_restart()
        test.expect(test.check_status('off',test.dut.at1))
        test.expect(test.check_status('off', test.dut.at2))

    def cleanup(test):
       pass

    def set_status(test, status,port):
        return port.send_and_verify('at^scfg="GPRS/RingOnIncomingData",{}'.format(status), 'OK')

    def check_status(test,expect_status,port):
        port.send_and_verify('at^scfg="GPRS/RingOnIncomingData"', 'OK')
        res = port.last_response
        if expect_status.lower() in res:
            return True
        else:
            return False



if "__main__" == __name__:
    unicorn.main()
