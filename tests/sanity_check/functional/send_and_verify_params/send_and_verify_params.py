# responsible: johann.suhr@thalesgroup.com
# location: Berlin
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
import time

class Test(BaseTest):
    """ Test for send_and_verify DSTL method """

    def setup(test):
        test.dut.dstl_detect()
        pass

    def run(test):
        # check SIM card status, enter SIM pin if locked
        test.dut.at1.send_and_verify('at+cpin?')
        if not 'READY' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('at+cpin=' + test.dut.sim.pin1)

        # test default expect parameter. The following send_and_verify call should return False.
        test.expect(not test.dut.at1.send_and_verify("ATR"))  # atat gets recognized as 'ata' but no call

        # test parameters of the send_and_verify method
        test.expect(test.dut.at1.send_and_verify("AT"))
        test.expect(test.dut.at1.send_and_verify("AT", expect=".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT", wait_for=".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT", timeout=2))
        test.expect(test.dut.at1.send_and_verify("AT", wait_after_send=1))
        test.expect(test.dut.at1.send_and_verify("AT", append=True))

        # test expect
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*OK.*",
            ".*OK.*"))

        # test wait_for

        # deregister from network
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CREG=2", ".*OK.*"))

        # force new network registration
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0", wait_for=".*\+CREG:.*"))

        # wait for with timeout
        t = time.time()
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*", ".*\+CREG: 2.*", timeout=10))
        delta = time.time() - t
        # test.expect(delta < 10)
        test.log.info("Time passed: {:.2f}".format(delta))

        # test wait_after_send
        t = time.time()
        test.dut.at1.send_and_verify("AT", wait_after_send=1)
        test.expect(time.time() - t >= 1)

        # test append=True
        test.dut.at1.send_and_verify("AT")
        test.dut.at1.send_and_verify("AT", append=True)
        test.expect(test.dut.at1.get_last_response().count("OK") == 2)

        # test append=False
        test.dut.at1.send_and_verify("AT")
        test.dut.at1.send_and_verify("AT", append=False)
        test.expect(test.dut.at1.get_last_response().count("OK") == 1)

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
