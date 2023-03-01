#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0091779.001 - TpAts5Basic

import unicorn
import random

from core.basetest import BaseTest

from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.auxiliary import init


class TpATS5Basic(BaseTest):

    def setup(test):
        test.log.info("1. Restore to default configurations ")
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.log.info("2. Enable SIM PIN lock before testing  ")
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(2)
        pass

    def run(test):
        defautlValue_ATS5 = 8
        if (test.dut.project == 'VIPER'):
            test.log.info("Command ATS5 is dummy, and has no effect on module behavior. ")
            test.log.info("Check only, if the retrun valus is alsways 08")
            test.expect(test.dut.at1.send_and_verify("ATS5=70", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("ATS5?", ".*008.*OK.*"))
        else:
            test.log.info("1. test: Query default value of ATS5 without PIN ")
            if (test.dut.project.lower() == "serval") or (test.dut.project.lower() == "marlin"):
                test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(defautlValue_ATS5)))
            else:
                test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(defautlValue_ATS5)))

            test.log.info("2. test: Set ATS5 with some random value 0-127 and query the value")
            for x in range(6):
                value = random.randint(0, 127)
                test.expect(test.dut.at1.send_and_verify("ATS5=" + str(value), ".*OK.*"))
                if (test.dut.project.lower() == "serval") or (test.dut.project.lower() == "marlin"):
                    test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(defautlValue_ATS5)))
                else:
                    test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(value)))

            test.log.info("3. test: Set ATS5 with incorrect value ")
            for incorrectValue in ["128", "-1", "A", "a", "<", ">"]:
                test.expect(test.dut.at1.send_and_verify("ATS5=" + incorrectValue, ".*ERROR.*"))
                if (test.dut.project.lower() == "serval") or (test.dut.project.lower() == "marlin"):
                    test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(defautlValue_ATS5)))
                else:
                    test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(value)))

            test.expect(test.dut.dstl_enter_pin())
            test.log.info("Wait a while after input PIN code")

            test.log.info("4. test: Query default value of ATS5 after input PIN ")
            if (test.dut.project.lower() == "serval") or (test.dut.project.lower() == "marlin"):
                test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(defautlValue_ATS5)))
            else:
                test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(value)))

            test.log.info("5. test: Set ATS5 with some random value 0-127 and query the value")
            for x in range(6):
                value = random.randint(0, 127)
                test.expect(test.dut.at1.send_and_verify("ATS5=" + str(value), ".*OK.*"))
                if (test.dut.project.lower() == "serval") or (test.dut.project.lower() == "marlin"):
                    test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(defautlValue_ATS5)))
                else:
                    test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(value)))

            test.log.info("6. test: Set ATS5 with incorrect value ")
            for incorrectValue in ["128", "-1", "A", "a", "<", ">"]:
                test.expect(test.dut.at1.send_and_verify("ATS5=" + incorrectValue, ".*ERROR.*"))
                if (test.dut.project.lower() == "serval") or (test.dut.project.lower() == "marlin"):
                    test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(defautlValue_ATS5)))
                else:
                    test.expect(test.dut.at1.send_and_verify("ATS5?", ".*{}.*OK.*".format(value)))

    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()
