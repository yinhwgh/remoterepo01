#author: hui.yu@thalesgroup.com
#location: Dalian
#TC0084440.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        pass

    def run(test):
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('at+cops?', expect='+COPS: 0,0,"CHINA MOBILE",7'))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,3,"+8613604944916",129,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2,,,1', expect='+CCFC: 1,1,"+8613604944916",145'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2,,,255', expect='+CCFC: 1,1,"+8613604944916",145'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,0,,,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2,,,1', expect='+CCFC: 0,1,"+8613604944916",145'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2,,,255', expect='+CCFC: 0,1,"+8613604944916",145'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,1,,,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2,,,255', expect='+CCFC: 1,1,"+8613604944916",145'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,4,,,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2,,,1', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,3,"+8613604944916",129,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2,,,1', expect='+CCFC: 1,1,"+8613604944916",145'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2,,,255', expect='+CCFC: 1,1,"+8613604944916",145'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,0,,,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2,,,1', expect='+CCFC: 0,1,"+8613604944916",145,,,'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2,,,255', expect='+CCFC: 0,1,"+8613604944916",145,,,'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,1,,,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2,,,255', expect='+CCFC: 1,1,"+8613604944916",145'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,2,,,255', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,4,,,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2,,,1', expect='+CCFC: 0,1'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2,,,255', expect='+CCFC: 0,1'))

    def cleanup(test):
        pass


if '__main__' == __name__:
    unicorn.main()
