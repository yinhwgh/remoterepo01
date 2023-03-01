#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0105163.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
import serial


class Test(BaseTest):
    '''
    TC0105163.002 - at_icf_multiplex
    '''

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step("1.Check Mux driver is ready on module")
        try:
            test.dut.at1.close()
            test.expect(test.dut.mux_1.send_and_verify('AT', 'OK'))
        except:
            test.expect(False, critical=True, msg='MUX Port not work, please check')

        test.log.step("2.Check current icf")
        test.expect(test.dut.mux_1.send_and_verify('AT+ICF?','ICF: 3\s+OK'))
        test.log.step("3.Set icf to 7N1, at+icf=5,1")
        test.expect(test.dut.mux_1.send_and_verify('AT+ICF=5,1', 'OK'))
        test.log.step("4. Execute at&w to store in user defined profile")
        test.expect(test.dut.mux_1.send_and_verify("at&w", "OK"))
        test.log.step("5. Restart module")
        test.dut.mux_1.send_and_verify("at+cfun=1,1", "OK")

        test.log.step("6. In mux port, check icf setting")
        test.dut.mux_1.close()
        test.sleep(60)
        test.dut.mux_1.open()
        test.expect(test.dut.mux_1.send_and_verify('AT+ICF?', 'ICF: 5,1\s+OK'))

        test.log.step("7. Checked 7N1 in yaat, "
                      "and transfer some at commands verify it is still OK to transfer")
        test.dut.mux_1.reconfigure({"bytesize": serial.SEVENBITS,
                                  "parity": serial.PARITY_EVEN,
                                  "stopbits": serial.STOPBITS_ONE})
        test.dut.mux_1.close()
        test.sleep(60)
        test.dut.mux_1.open()
        test.dut.mux_1.send_and_verify('ati','OK')
        test.expect(test.dut.mux_1.send_and_verify("at+icf=3", "OK"))
        test.expect(test.dut.mux_1.send_and_verify("at&w", "OK"))

        test.log.step("8. Close mux port and open UART port and check icf setting has no effect")
        test.dut.mux_1.close()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT+ICF?', 'ICF: 3\s+OK'))
        test.expect(test.dut.at1.send_and_verify('ati','OK'))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("at&F", "OK"))
        test.expect(test.dut.at1.send_and_verify("at&w", "OK"))
        test.dut.at1.send_and_verify("at+cfun=1,1", "OK")
        test.dut.at1.wait_for("SYSSTART")
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+icf?", "ICF: 3\s+OK"))


if "__main__" == __name__:
    unicorn.main()

