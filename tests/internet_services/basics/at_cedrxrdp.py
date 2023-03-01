#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC0096204.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network



class cedrxrdp(BaseTest):
    def setup(test):
        test.dut.dstl_detect()


    def run(test):
        test.log.info("1. test: check AT+CEDRXRDP without PIN code")
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP=?', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP', '.*\\+CEDRXRDP: ([245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\"|0).*OK.*'))

        test.log.info("2. test: enter PIN code")
        test.expect(test.dut.dstl_register_to_network())

        test.log.info("3. test: check test command AT+CEDRXRDP")
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP=?', '.*OK.*'))

        test.log.info("4. test: check read command AT+CEDRXRDP")
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP', '.*\\+CEDRXRDP: (0|[245],\\"[01]{4}\\",\\"[01]{4}\\",\\"[01]{4}\\").*OK.*'))

        test.log.info("5. test: Invalid value should be return error")
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP=', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP?', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP=5', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP=a', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP=@', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP=~', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXRDP=#', '.*ERROR.*'))


        test.log.info('*** END TEST ***')

    def cleanup(test):
        pass

if(__name__ == "__main__"):
    unicorn.main()
