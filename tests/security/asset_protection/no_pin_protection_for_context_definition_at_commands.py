#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC0102514.001
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary.devboard import devboard


class no_pin_protection_for_context_definition_at_commands(BaseTest):
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.info("1. test: check test command without SIM card ")
        test.expect(test.dut.dstl_remove_sim())
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?', '.*\\+CGDCONT: \\(1\\-16\\),"IP",,,\\(0\\-2\\),\\(0\\-4\\).*\\+CGDCONT: \\(1\\-16\\),"IPV6",,,\\(0\\-2\\),\\(0\\-4\\).*\\+CGDCONT: \\(1\\-16\\),"IPV4V6",,,\\(0\\-2\\),\\(0\\-4\\).*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', '.*\\+CGDCONT:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IPV4V6","radius"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=?', '.*\\^SGAUTH: \\(1\\-16\\),\\(0\\-2\\),,.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH?', '.*\\^SGAUTH:.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=1,1,"gemalto","gemalto"', '.*OK.*'))

        test.log.info("2. test: check test command without SIM card under airplane mode ")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', '(.*OK.*\\^SYSSTART AIRPLANE MODE.*|.*OK.*)'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?','.*\\+CGDCONT: \\(1\\-16\\),"IP",,,\\(0\\-2\\),\\(0\\-4\\).*\\+CGDCONT: \\(1\\-16\\),"IPV6",,,\\(0\\-2\\),\\(0\\-4\\).*\\+CGDCONT: \\(1\\-16\\),"IPV4V6",,,\\(0\\-2\\),\\(0\\-4\\).*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', '.*\\+CGDCONT:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IPV4V6","radius"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=?', '.*\\^SGAUTH: \\(1\\-16\\),\\(0\\-2\\),,.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH?', '.*\\^SGAUTH:.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=1,1,"gemalto","gemalto"', '.*OK.*'))


        test.log.info("3. test: check test command without PIN: insert sim card, but not enter pin code ")
        test.expect(test.dut.dstl_insert_sim())
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?', '.*\\+CGDCONT: \\(1\\-16\\),"IP",,,\\(0\\-2\\),\\(0\\-4\\).*\\+CGDCONT: \\(1\\-16\\),"IPV6",,,\\(0\\-2\\),\\(0\\-4\\).*\\+CGDCONT: \\(1\\-16\\),"IPV4V6",,,\\(0\\-2\\),\\(0\\-4\\).*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', '.*\\+CGDCONT:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IPV4V6","radius"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=?', '.*\\^SGAUTH: \\(1\\-16\\),\\(0\\-2\\),,.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH?', '.*\\^SGAUTH:.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=1,1,"gemalto","gemalto"', '.*OK.*'))

        test.log.info("4. test: check test command without PIN under airplane mode ")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', '(.*OK.*\\^SYSSTART AIRPLANE MODE.*|.*OK.*)'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?','.*\\+CGDCONT: \\(1\\-16\\),"IP",,,\\(0\\-2\\),\\(0\\-4\\).*\\+CGDCONT: \\(1\\-16\\),"IPV6",,,\\(0\\-2\\),\\(0\\-4\\).*\\+CGDCONT: \\(1\\-16\\),"IPV4V6",,,\\(0\\-2\\),\\(0\\-4\\).*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', '.*\\+CGDCONT:.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IPV4V6","radius"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=?', '.*\\^SGAUTH: \\(1\\-16\\),\\(0\\-2\\),,.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH?', '.*\\^SGAUTH:.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=1,1,"gemalto","gemalto"', '.*OK.*'))

    def cleanup(test):
        pass

if(__name__ == "__main__"):
    unicorn.main()
