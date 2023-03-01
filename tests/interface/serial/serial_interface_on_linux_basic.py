#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0104360.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary import restart_module


class Test(BaseTest):
    """
    TC0104360.001 SerialInterfaceonLinuxBasic
    Check Serial Interface ASC0 and ASC1 on Linux.
    responsible: mariusz.wojcik@globallogic.com
    location: Wroclaw
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.step("1. Check that module is present as ttySx device.")
        test.expect("ttyUsb0" in test.os.execute('ls /dev/'))

        test.log.step("2. Open ASC0 (ttySx) in terminal and send any AT-Command.")
        test.expect(test.dut.at1.send_and_verify("AT", "OK"))

        test.log.step("3. Restart module.")
        test.expect(test.dut.dstl_restart())

        test.log.step("4. After restart, send any at-commands one more time.")
        test.expect(test.dut.at1.send_and_verify("AT", "OK"))

        test.log.step("5. Repeat step 1-4 for ASC1 interface.")
        test.dut.at1 = test.dut.at2

        test.log.step("1. Check that module is present as ttySx device.")
        test.log.info("Repeating step for ASC1 interface")
        test.expect("ttyUsb1" in test.os.execute('ls /dev/'))

        test.log.step("2. Open ASC1 (ttySx) in terminal and send any AT-Command.")
        test.log.info("Repeating step for ASC1 interface")
        test.expect(test.dut.at1.send_and_verify("AT", "OK"))

        test.log.step("3. Restart module.")
        test.log.info("Repeating step for ASC1 interface")
        test.expect(test.dut.dstl_restart())

        test.log.step("4. After restart, send any at-commands one more time.")
        test.log.info("Repeating step for ASC1 interface")
        test.expect(test.dut.at1.send_and_verify("AT", "OK"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
