#responsible: johann.suhr@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
from datetime import datetime, timedelta
from dstl.auxiliary import restart_module

from dstl.auxiliary import init


class Test(BaseTest):
    """ Stability test to check unicorns behaviour under long-term use. """

    def setup(test):
        test.dut.dstl_detect()
        pass

    def run(test):
        stop_date = datetime.now() + timedelta(hours=0, minutes=30)

        iteration = 0
        while datetime.now() < stop_date:
            test.log.info(f'{"*" * 20} Last iteration will start before ' + stop_date.strftime('%d-%m-%Y,%H:%M:%S'))
            test.log.info(f'{"*" * 20} Test iteration: {iteration:05}')
            test.expect(test.dut.at1.send_and_verify("AT"))
            test.dut.dstl_restart()
            iteration += 1

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
