#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0000399.001

import unicorn
from core.basetest import BaseTest


class CpasAllg(BaseTest):
    """
        TC0000399.001 - CpasAllg
        Check availability of CPAS command and output for wrong parameter setting.
    """
    def setup(test):
        pass

    def run(test):
        # Test response for CMEE 1, 2
        for i in range(1, 3):
            test.log.info("{}.1 Get OK response for valid commands for CMEE : {}".format(str(i), str(i)))
            test.dut.at1.send_and_verify("AT+CMEE={}".format(str(i)), ".*OK.*")
            test.expect(test.dut.at1.send_and_verify("AT+CMEE?", "\s\+CMEE: {}\s".format(str(i))))
            test.expect(test.dut.at1.send_and_verify("AT+CPAS=?", "\sOK\s"))
            test.expect(test.dut.at1.send_and_verify("AT+CPAS", "\sOK\s"))
            test.log.info("{}.2 Get ERROR response for invalid commands for CMEE : {}".format(str(i), str(i)))
            test.expect(test.dut.at1.send_and_verify("AT+CPAS?", "\s\+CME ERROR:\s"))
            test.expect(test.dut.at1.send_and_verify("AT+CPAS=1", "\s\+CME ERROR:\s"))
            test.expect(test.dut.at1.send_and_verify("AT+CPAS1", "\s\+CME ERROR:\s"))
            test.expect(test.dut.at1.send_and_verify("AT+CPAS=76", "\s\+CME ERROR:\s"))
            test.expect(test.dut.at1.send_and_verify("AT+CPAS=*#", "\s\+CME ERROR:\s"))
            test.expect(test.dut.at1.send_and_verify("AT+CPASZ", "\s\+CME ERROR:\s"))


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

