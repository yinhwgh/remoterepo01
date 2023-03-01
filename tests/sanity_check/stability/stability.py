#responsible: johann.suhr@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
from datetime import datetime, timedelta

from dstl.auxiliary import init


class Test(BaseTest):
    """ Stability test to check unicorns behaviour under long-term use. """

    def setup(test):
        test.dut.dstl_detect()
        pass

    def run(test):
        stop_date = datetime.now() + timedelta(minutes=2)

        iteration = 0
        while datetime.now() < stop_date:
            test.log.info(f'{"*" * 20} Last iteration will start before ' + stop_date.strftime('%d-%m-%Y,%H:%M:%S'))
            test.log.info(f'{"*" * 20} Test iteration: {iteration:05}')
            test.expect(test.dut.at1.send_and_verify("AT+CFUN?"))
            test.expect(test.dut.at1.send_and_verify("AT+CFUN=4", wait_after_send=3))
            test.expect(test.dut.at1.send_and_verify("AT+CFUN?"))
            test.expect(test.dut.at1.send_and_verify("AT+CFUN=1", wait_after_send=3))
            test.expect(test.dut.at1.send_and_verify("AT+CFUN?"))
            iteration += 1

            for x in range(100):
                test.expect(test.dut.at1.send_and_verify("AT"))

            test.sleep(2)

            for x in range(100):
                test.expect(test.dut.at1.send_and_verify("AT"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
