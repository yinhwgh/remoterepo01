#author: jin.li@thalesgroup.com
#location: Dalian
#TC0104056.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module

class Test(BaseTest):
    """
    TC0104056.001 -  TpAtScfgAutoAttach_LTE
    Subscribers: 1
    Debugged: Viper
    Intention: When PS Power up attach disable,check whether it could manual register to LTE or not
    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/AutoAttach","disabled"', expect='OK'))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/AutoAttach"', expect='^SCFG: "GPRS/AutoAttach","disabled"'))
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        test.expect(not test.dut.dstl_register_to_lte())
        test.expect(test.dut.at1.send_and_verify('at+cgatt?', expect='+CGATT: 0',timeout=5))
        test.expect(test.dut.at1.send_and_verify('at+cgatt=1', expect='OK'))
        test.expect(test.dut.dstl_register_to_lte())
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*[+]COPS:.*,.*,.*,7.*OK.*"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.dstl_restart())

if '__main__' == __name__:
    unicorn.main()
