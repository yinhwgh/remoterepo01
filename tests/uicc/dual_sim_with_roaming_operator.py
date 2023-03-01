#author: cong.hu@thalesgroup.com
#location: Dalian
#TC0103996.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import check_urc
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.call import setup_voice_call
from dstl.security import set_sim_waiting_for_pin1

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.r1.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.dstl_restart())
        test.expect(test.r1.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='.*OK.*'))
        test.expect(test.r1.at1.send_and_verify('at+cmee=2', expect='.*OK.*'))
        test.expect(test.r1.at1.send_and_verify('AT+CREG=1', expect='.*OK.*'))
        test.expect(test.r1.dstl_enter_pin())
        test.expect(test.r1.dstl_check_urc('.*\+CREG: 1.*|.*\+CREG: 5.*'))
        test.expect(test.r1.at1.send_and_verify('AT+CSMS=1', expect='.*OK.*'))
        test.expect(test.r1.at1.send_and_verify('AT+CNMI=2,1', expect='.*OK.*'))
        test.expect(test.r1.at1.send_and_verify('AT+CMGF=1', expect='.*OK.*'))

    def run(test):
        dut_phone_num = test.dut.sim.nat_voice_nr
        dut_phone_num2 = test.dut.sim2.int_voice_nr
        r1_phone_num = test.r1.sim.int_voice_nr

        test.log.info('1.Enable CREG URC for DUT.')
        test.expect(test.dut.at1.send_and_verify('AT+CREG=1', expect='.*OK.*'))

        test.log.info('2.Check PIN status.')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', expect='\s+\+CPIN: SIM PIN\s+OK.*'))

        test.log.info('3.Enter PIN.')
        test.expect(test.dut.dstl_enter_pin())

        test.log.info('4.Register to network.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', expect='.*OK.*'))

        test.log.info('5.Wait for the module register to home network and monitor CREG URC.')
        test.expect(test.dut.dstl_check_urc('.*\+CREG: 1.*'))

        test.log.info('6.Read IMSI of DUT sim1.')
        test.expect(test.dut.at1.send_and_verify('AT+CIMI', expect='.*OK.*'))

        test.log.info('7.Set SMS service for DUT.')
        test.expect(test.dut.at1.send_and_verify('AT+CSMS=1', expect='.*OK.*'))

        test.log.info('8.DUT set the  SMS Event Reporting Configuration.')
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=2,1', expect='.*OK.*'))

        test.log.info('9.DUT set short message format as TEXT.')
        test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', expect='.*OK.*'))

        test.log.info('10.Wait 10 seconds.')
        test.sleep(10)

        test.log.info('11.Initiate a call to remote module.')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1,r1_phone_num))

        test.log.info('12.Let the voice call last 20 seconds.')
        test.sleep(20)

        test.log.info('13.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*'))

        test.log.info('14.DUT send short message to remote.')
        test.expect(dstl_send_sms_message(test.dut, r1_phone_num))

        test.log.info('15.Remote wait for the URC for short message.')
        test.expect(test.r1.at1.wait_for(".*CMTI.*", timeout=120))
        #Switch SIM card to slot 2.
        test.log.info('16.DUT switch to roaming sim card.')
        test.expect(test.dut.at1.send_and_verify('at^scfg="SIM/CS",3', expect='.*OK.*'))

        test.log.info('17.With for the sim init.')
        test.sleep(20)

        test.log.info('18.Enter PIN.')
        test.expect(test.dut.dstl_enter_pin())

        test.log.info('19.Wait for the module register to network and monitor CREG URC.')
        test.expect(test.dut.dstl_check_urc('.*\+CREG: 5.*'))

        test.log.info('20.DUT setup a MO call to remote.')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1,r1_phone_num))

        test.log.info('21.Let the voice call last 20 seconds.')
        test.sleep(20)

        test.log.info('22.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*'))

        test.log.info('23.Wait 5 seconds.')
        test.sleep(5)

        test.log.info('24.Remote call DUT.')
        test.expect(test.r1.dstl_voice_call_by_number(test.dut,dut_phone_num2))

        test.log.info('24.Let the voice call last 20 seconds.')
        test.sleep(20)

        test.log.info('25.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*'))

        test.log.info('26.Wait 5 seconds.')
        test.sleep(5)
        #Short message function check
        test.log.info('27.DUT send short message to remote.')
        test.expect(test.dut.dstl_send_sms_message(r1_phone_num, device_sim=test.dut.sim2))

        test.log.info('28.Remote wait for the URC for short message.')
        test.expect(test.r1.at1.wait_for("\+CMTI:.*"))

        test.log.info('29.Remote send short message to DUT.')
        test.expect(test.r1.dstl_send_sms_message(dut_phone_num2))

        test.log.info('29.DUT wait for the URC for short message.')
        test.expect(test.dut.at1.wait_for("\+CMTI:.*", timeout=120))

        test.log.info('30.Test internet service-TCP.')
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IPV4V6","internet"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,SrvType,socket', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,conId,1', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,address,"socktcp://182.92.198.110:9010"', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISA=1,1', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^siso=1', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISW=1,8', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('test tcp', expect='.*OK.*'))
        test.expect(test.dut.wait_for("\s+\^SISR: 1,1.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SISR=1,8', expect='\s+test tcp.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SISC=1', expect='.*OK.*'))

    def cleanup(test):
        test.log.info('Switch back to the first sim slot.')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="SIM/CS","0"', expect='.*OK.*'))

if '__main__' == __name__:
    unicorn.main()
