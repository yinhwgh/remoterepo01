#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0095088.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect

class Test(BaseTest):
    '''
    TC0095088.001 - ATI8_Original
    To check if public AT command ATI8 displays the hardcoded Customization Revision ("C-REVISION")
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', expect='OK'))

    def run(test):
        test.log.step('1.Send ATI8 command')
        test.expect(test.dut.at1.send_and_verify('ATI8', expect='.*C-REVISION 00000.00.*'))
        test.log.step('2.Send ATI1I8 command')
        test.expect(test.dut.at1.send_and_verify('ATI1I8', expect='.*A-REVISION [0|9][0|1|9].000.\d\d\s+.*C-REVISION 00000.00\\s+.*'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
