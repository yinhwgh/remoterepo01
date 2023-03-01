#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0105164.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
import serial

class Test(BaseTest):
    '''
    TC0105164.002 - icf_sbnw_sbnr_cross
    '''

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        hex_to_write='20000000643E37BC3BBA722467A0F614D6D0DE57A723E893CD1133D75590726B33A719FB'
        hex_to_verify='20000000643E37BC3BBA722467A0F614D6D0DE57A723E893CD1133D7.*OK.*'

        test.log.step("1.Check current icf")
        test.expect(test.dut.at1.send_and_verify('AT+ICF?','ICF: 3\s+OK'))
        test.log.step("2.Set icf to 7N1, at+icf=5,1")
        test.expect(test.dut.at1.send_and_verify('AT+ICF=5,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify("at&w", "OK"))
        test.dut.at1.send_and_verify("at+cfun=1,1", "OK")
        test.sleep(0.2)
        test.dut.at1.reconfigure({"bytesize": serial.SEVENBITS,
                                  "parity": serial.PARITY_EVEN,
                                  "stopbits": serial.STOPBITS_ONE})
        test.dut.at1.wait_for("SYSSTART")
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT+ICF?', 'ICF: 5,1\s+OK'))

        test.log.step("3. Writing data to EFS by at^sbnw ")
        test.expect(test.dut.at1.send_and_verify('AT^SBNW="efs","/data/new.txt",2', '.*CONNECT.*',
                                                 wait_for='CONNECT'))
        test.expect(test.dut.at1.send_and_verify(hex_to_write, 'EFS: END OK\s+OK'))

        test.log.step("4. Read data from EFS by another fixed icf")
        test.expect(test.dut.at1.send_and_verify('AT+ICF=2,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify("at&w", "OK"))
        test.dut.at1.send_and_verify("at+cfun=1,1", "OK")
        test.sleep(0.2)
        test.dut.at1.reconfigure({"bytesize": serial.EIGHTBITS,
                                  "parity": serial.PARITY_ODD,
                                  "stopbits": serial.STOPBITS_ONE})
        test.dut.at1.wait_for("SYSSTART")
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT+ICF?', 'ICF: 2,0\s+OK'))
        test.expect(test.dut.at1.send_and_verify('at^sbnr="efs","/data/new.txt"', hex_to_verify))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("at&F", "OK"))
        test.expect(test.dut.at1.send_and_verify("at&w", "OK"))
        test.dut.at1.send_and_verify("at+cfun=1,1", "OK")
        test.sleep(0.2)
        test.dut.at1.reconfigure({"bytesize": serial.EIGHTBITS,
                                  "parity": serial.PARITY_NONE,
                                  "stopbits": serial.STOPBITS_ONE})
        test.dut.at1.wait_for("SYSSTART")
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+icf?", "ICF: 3\s+OK"))


if "__main__" == __name__:
    unicorn.main()
