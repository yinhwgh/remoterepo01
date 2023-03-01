#author: cong.hu@thalesgroup.com
#location: Dalian
#TC0105067.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.security import set_sim_waiting_for_pin1

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', expect='.*OK.*'))
        test.sleep(10)

    def run(test):
        test.log.info('1.Check PIN status.')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', expect='\s+\+CPIN: SIM PIN\s+OK.*'))

        test.log.info('2.Check test command without PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=?', expect='\s+\+CME ERROR: SIM PIN required.*'))

        test.log.info('3.Check read command without PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP?', expect='\s+\+CME ERROR: SIM PIN required.*'))

        test.log.info('4.Check write command without PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=1', expect='\s+\+CME ERROR: SIM PIN required.*'))

        test.log.info('5.Try to Read the CEVDP setting without PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP?', expect='\s+\+CME ERROR: SIM PIN required.*'))

        test.log.info('6.Enter PIN.')
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)

        test.log.info('7.Check test command with PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=?', expect='\s+\+CEVDP: \(1-4\)\s+OK.*'))

        test.log.info('8.Check read command with PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP?', expect='\s+\+CEVDP: 3\s+OK.*'))

        test.log.info('9.Check write command with PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=2', expect='.*OK.*'))

        test.log.info('10.Read the value wrote in last step.')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP?', expect='\s+\+CEVDP: 2\s+OK.*'))

        test.log.info('11.Check write command with PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=1', expect='.*OK.*'))

        test.log.info('12.Read the value wrote in last step.')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP?', expect='\s+\+CEVDP: 1\s+OK.*'))

        test.log.info('13.Check write command with PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=2', expect='.*OK.*'))

        test.log.info('14.Read the value wrote in last step.')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP?', expect='\s+\+CEVDP: 2\s+OK.*'))

        test.log.info('15.Check write command with PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=3', expect='.*OK.*'))

        test.log.info('16.Read the value wrote in last step.')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP?', expect='\s+\+CEVDP: 3\s+OK.*'))

        test.log.info('17.Check write command with PIN.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=4', expect='.*OK.*'))

        test.log.info('18.Read the value wrote in last step.')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP?', expect='\s+\+CEVDP: 4\s+OK.*'))

        test.log.info('19.Check invalid number -1.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=-1', expect='.*ERROR.*'))

        test.log.info('20.Check invalid number 5.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=5', expect='.*ERROR.*'))

        test.log.info('21.Check invalid number 6.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=6', expect='.*ERROR.*'))

        test.log.info('22.Check invalid number 7.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=7', expect='.*ERROR.*'))

        test.log.info('23.Check invalid number 8.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=8', expect='.*ERROR.*'))

        test.log.info('24.Check invalid number 9.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=9', expect='.*ERROR.*'))

        test.log.info('25.Check invalid number 65535.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=65535', expect='.*ERROR.*'))

        test.log.info('26.Check invalid alphabeta a.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=a', expect='.*ERROR.*'))

        test.log.info('27.Check invalid alphabeta b.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=b', expect='.*ERROR.*'))

        test.log.info('28.Check invalid alphabeta c.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=c', expect='.*ERROR.*'))

        test.log.info('29.Check invalid alphabeta D.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=D', expect='.*ERROR.*'))

        test.log.info('30.Check invalid alphabeta E.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=E', expect='.*ERROR.*'))

        test.log.info('31.Check invalid alphabeta F.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=F', expect='.*ERROR.*'))

        test.log.info('32.Check invalid special character "!".')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=!', expect='.*ERROR.*'))

        test.log.info('33.Check invalid special character "@".')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=@', expect='.*ERROR.*'))

        test.log.info('34.Check invalid special character "#".')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=#', expect='.*ERROR.*'))

        test.log.info('35.Check invalid special character "$".')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=$', expect='.*ERROR.*'))

        test.log.info('36.Check invalid special character "%".')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=%', expect='.*ERROR.*'))

        test.log.info('37.Check invalid special character "^".')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=^', expect='.*ERROR.*'))

        test.log.info('38.Check invalid special character "&".')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=&', expect='.*ERROR.*'))

        test.log.info('39.Check invalid special character "*".')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=*', expect='.*ERROR.*'))

        test.log.info('40.Check invalid special character "<".')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=<', expect='.*ERROR.*'))

        test.log.info('41.Check invalid special character ">".')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=>', expect='.*ERROR.*'))

        test.log.info('42.Change back to default value 3.')
        test.expect(test.dut.at1.send_and_verify('AT+CEVDP=3', expect='.*OK.*'))

    def cleanup(test):
        test.expect(test.dut.dstl_restart())


if '__main__' == __name__:
    unicorn.main()
