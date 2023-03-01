# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_at_queries

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):

    def setup(test):
        pass

    def run(test):

        test.dut.at1.send_and_verify("at+cpin?")
        if "READY" in test.dut.at1.last_response:
            pass
        else:
            res = test.dut.at1.send_and_verify("at+cpin=\"{}\"".format(test.dut.sim.pin1), "OK")
            test.expect(res, critical=True)
            test.sleep(10)

        test.dut.at1.send_and_verify("at+creg=2")
        test.dut.at1.send_and_verify("at+cgreg=2")
        check = test.attempt(test.dut.at1.send_and_verify, "at+creg=2", "OK")
        test.log.info(check)

        test.log.info("Checking network")
        test.dut.at1.send_and_verify("at+csq")
        res = test.dut.at1.send_and_verify("at+csq", ".*at\+csq.*OK.*")
        test.dut.at1.send_and_verify("at+cops?")
        test.dut.at1.send_and_verify("at+creg?")
        test.sleep(1.5)

        res = test.dut.at1.send_and_verify("at+copn", timeout = 30)
        test.expect("URUGUAY" in test.dut.at1.last_response)

        res = test.dut.at1.send_and_verify("at+cops=?", "OK", timeout = 120)
        test.expect("Orange" in test.dut.at1.last_response or "Vodafone" in test.dut.last_response)

        test.dut.at1.send_and_verify("at+cops=0", "OK", timeout = 60, append=True)
        test.dut.at1.send_and_verify("at+cops?", "OK", timeout = 60, append=True)

        test.dut.at1.append(True)
        for i in range(10):
            test.dut.at1.send_and_verify("at+cops=2", "OK", timeout = 60)
            test.dut.at1.send_and_verify("at+cops?", "OK", timeout = 60)

            test.sleep(5)
            test.dut.at1.send("at+cops=0")
            res = test.dut.at1.wait_for("CREG", timeout=90, append=True)

        res = test.dut.at1.send_and_verify("at+cfun=5", "OK", timeout = 60, append=True)
        test.sleep(2)
        res = test.dut.at1.send_and_verify("at+cfun=1", "OK", timeout = 60, append=True)
        test.sleep(2)

        test.log.info(test.dut.at1.last_response)

        test.dut.at1.append(False)

        for i in range(10):
            res = test.dut.at1.send_and_verify("ati", "OK")
            test.expect(res)
            test.dut.at1.close()
            test.dut.at1.open()
            res = test.dut.at1.send_and_verify("ati")
            test.expect(res)
            test.sleep(5)

    def cleanup(test):
        res = test.dut.at1.send_and_verify("at+cfun=1,1", expect = "OK", wait_for=".*SYSLOADING.*|.*SYSSTART.*", timeout = 120)
        test.dut.at1.wait_until_active()
        pass


if "__main__" == __name__:
    unicorn.main()
