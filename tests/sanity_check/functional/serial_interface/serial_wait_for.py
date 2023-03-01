# responsible: tomasz.witka@thalesgroup.com
# location: Wroclaw
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
import time

class Test(BaseTest):
    """ Test for wait_for serial method """

    def setup(test):
        pass
        

    def run(test):
        test.dut.at1.send_and_verify('at', expect='')
        test.dut.at1.send_and_verify('ate1')
        
        for i in range(9):
            res = test.dut.at1.send('at').wait_for('OK')
            test.expect(res)

        res = test.dut.at1.send('at+copn').wait_for('OK')
        test.expect(res)

        for i in range(9):
            test.dut.at1.send('at', end='')
        test.sleep(1)
        test.dut.at1.read()
        test.expect(9 * 'at' in test.dut.at1.last_response)

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()

