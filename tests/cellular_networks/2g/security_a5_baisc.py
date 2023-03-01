#author: cong.hu@thalesgroup.com
#location: Dalian
#TC0105065.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.security import set_sim_waiting_for_pin1

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()


    def run(test):
        test.log.step('1.a Power on the module, enable error report with "at+cmee=2"')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.log.step('1.b Check PIN status with "at+cpin?". If PIN is disabled, enable it')
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.log.step('1.c Check command without PIN')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', expect='\s+\+CPIN: SIM PIN\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5"', expect='\s+\^SCFG: \"Security/A5\",\"5\"\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",4', expect='\s+\^SCFG: \"Security/A5\",\"4\"\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",1', expect='\s+\^SCFG: \"Security/A5\",\"1\"\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",0', expect='\s+\^SCFG: \"Security/A5\",\"0\"\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",5', expect='\s+\^SCFG: \"Security/A5\",\"5\"\s+OK.*'))

        test.log.step('1.d Check command with PIN')
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5"', expect='\s+\^SCFG: \"Security/A5\",\"5\"\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",4', expect='\s+\^SCFG: \"Security/A5\",\"4\"\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",1', expect='\s+\^SCFG: \"Security/A5\",\"1\"\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",0', expect='\s+\^SCFG: \"Security/A5\",\"0\"\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",5', expect='\s+\^SCFG: \"Security/A5\",\"5\"\s+OK.*'))

        test.log.step('2.Check for invalid parameter')
        test.log.step('2.a Check invalid number(-1,2,3,6,7,8,9,65535)')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",-1', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",2', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",3', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",6', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",7', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",8', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",9', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",65535', expect='\s+\+CME ERROR: invalid index.*'))

        test.log.step('2.b Check invalid alphabeta(a,b,c,D,E,F)')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",-1', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",a', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",b', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",c', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",D', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",E', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",F', expect='\s+\+CME ERROR: invalid index.*'))

        test.log.step('2.c Check invalid special character(!,@,#,$,%,^,&,*,<,>,?)')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",!', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",@', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",#', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",$', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",%', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",^', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",&', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",*', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",<', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",>', expect='\s+\+CME ERROR: invalid index.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",?', expect='\s+\+CME ERROR: invalid index.*'))

        test.log.step('3. Change back to the default setting.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5",5', expect='\s+\^SCFG: \"Security/A5\",\"5\"\s+OK.*'))

    def cleanup(test):
        test.log.step('Check if the default value is restored.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5"', expect='\s+\^SCFG: \"Security/A5\",\"5\"\s+OK.*'))


if '__main__' == __name__:
    unicorn.main()
