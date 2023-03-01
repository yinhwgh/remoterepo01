#author: cong.hu@thalesgroup.com
#location: Dalian
#TC0095134.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary import check_urc
from dstl.call import setup_voice_call
from dstl.security import set_sim_waiting_for_pin1

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='.*OK.*'))
        test.expect(test.r1.at1.send_and_verify('at+cmee=2', expect='.*OK.*'))
        test.dut.dstl_set_sim_waiting_for_pin1()

        test.r1.dstl_set_sim_waiting_for_pin1()

        test.expect(test.r1.dstl_restart())
        test.expect(test.r1.at1.send_and_verify('at+creg=1', expect='.*OK.*'))
        test.expect(test.r1.dstl_enter_pin())
        test.expect(test.r1.dstl_check_urc('.*\+CREG: 1.*'))

    def run(test):
        dut_phone_num = test.dut.sim.nat_voice_nr
        r1_phone_num = test.r1.sim.nat_voice_nr

        test.log.info('######## Step 1.Restart module.')
        test.expect(test.dut.dstl_restart())

        test.log.info('######## Step 2.Enable IMS service on DUT.')
        test.expect(test.dut.at1.send_and_verify('at^scfg="MEopMode/IMS","1"', expect='.*OK.*'))

        test.log.info('######## Step 3.Define PDP context.')
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=2,"IPV6","IMS","",0,0,0,0,1,0', expect='.*OK.*'))

        test.log.info('######## Step 4.Restart module.')
        test.expect(test.dut.dstl_restart())

        test.log.info('######## Step 5.Enable CREG URC.')
        test.expect(test.dut.at1.send_and_verify('at+creg=1', expect='.*OK.*'))
        test.sleep(10)

        test.log.info('######## Step 6.Enter PIN for DUT.')
        test.expect(test.dut.dstl_enter_pin())

        test.log.info('######## Step 7.Wait for the module register to the network.')
        test.expect(test.dut.dstl_check_urc('.*\+CREG: 1.*'))

        test.log.info('######## Step 8.Check PDP context definition.')
        test.expect(test.dut.at1.send_and_verify('at+cgdcont?', expect='.*OK.*'))

        test.log.info('######## Step 9.Check which PDP contexts are active.')
        test.expect(test.dut.at1.send_and_verify('at+cgact?', expect='.*OK.*'))

        test.log.info('######## Step 10.Config voice domain preference to "CS voice only".')
        test.expect(test.dut.at1.send_and_verify('at+cevdp=1', expect='.*OK.*'))
        test.sleep(5)
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('at+creg=1', expect='.*OK.*'))
        test.sleep(10)
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_urc('.*\+CREG: 1.*'))
        test.expect(test.dut.at1.send_and_verify('at+cevdp?', expect='\s+\+CEVDP: 1\s+.*OK.*'))
        test.sleep(15)

        test.log.info('######## Step 11.Check IMS voice call availability status.')
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='.*\+CAVIMS: 0.*'))

        test.log.info('######## Step 12.Make MO voice call to remote.')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1,r1_phone_num))
        test.sleep(20)

        test.log.info('######## Step 13.Check call type. It should be CS call. The module fallback to GSM or UTRAN.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*\+COPS: 0,0,\".*\",0|2|3|4|6.*'))

        test.log.info('######## Step 14.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('at+chup', expect='.*OK.*'))
        test.sleep(5)

        test.log.info('######## Step 15.Use remote to call DUT - MT voice call.')
        test.expect(test.r1.dstl_voice_call_by_number(test.dut,dut_phone_num))
        test.sleep(20)

        test.log.info('######## Step 16.Check call type. It should be VoLTE. The module still registered to EUTRAN.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*\+COPS: 0,0,\".*\",0|2|3|4|6.*'))

        test.log.info('######## Step 17.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('at+chup', expect='.*OK.*'))
        test.sleep(5)

        test.log.info('######## Step 18.Config voice domain preference to "CS Voice preferred, IMS PS Voice as secondary".')
        test.expect(test.dut.at1.send_and_verify('at+cevdp=2', expect='.*OK.*'))
        test.sleep(5)
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('at+creg=1', expect='.*OK.*'))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_urc('.*\+CREG: 1.*'))
        test.expect(test.dut.at1.send_and_verify('at+cevdp?', expect='\s+\+CEVDP: 2\s+.*OK.*'))
        test.sleep(15)

        test.log.info('######## Step 19.Check IMS voice call availability status.')
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='.*\+CAVIMS: 0.*'))

        test.log.info('######## Step 20.Make MO voice call to remote.')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1,r1_phone_num))
        test.sleep(20)

        test.log.info('######## Step 21.Check call type. It should be CS call. The module fallback to GSM or UTRAN.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*\+COPS: 0,0,\".*\",0|2|3|4|6.*'))

        test.log.info('######## Step 22.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('at+chup', expect='.*OK.*'))
        test.sleep(5)

        test.log.info('######## Step 23.Use remote to call DUT - MT voice call.')
        test.expect(test.r1.dstl_voice_call_by_number(test.dut,dut_phone_num))
        test.sleep(20)

        test.log.info('######## Step 24.Check call type. It should be CS call. The module fallback to GSM or UTRAN.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*\+COPS: 0,0,\".*\",0|2|3|4|6.*'))

        test.log.info('######## Step 25.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('at+chup', expect='.*OK.*'))
        test.sleep(5)

        test.log.info('######## Step 26.Config voice domain preference to "IMS PS Voice preferred, CS Voice as secondary".')
        test.expect(test.dut.at1.send_and_verify('at+cevdp=3', expect='.*OK.*'))
        test.sleep(5)
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('at+creg=1', expect='.*OK.*'))
        test.sleep(10)
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_urc('.*\+CREG: 1.*'))
        test.expect(test.dut.at1.send_and_verify('at+cevdp?', expect='\s+\+CEVDP: 3\s+.*OK.*'))
        test.sleep(15)

        test.log.info('######## Step 27.Check IMS voice call availability status.')
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='.*\+CAVIMS: 1.*'))

        test.log.info('######## Step 28.Make MO voice call to remote.')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1,r1_phone_num))
        test.sleep(20)

        test.log.info('######## Step 29.Check call type. It should be VoLTE. The module still registered to EUTRAN.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*\+COPS: 0,0,\".*\",7.*'))

        test.log.info('######## Step 30.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('at+chup', expect='.*OK.*'))
        test.sleep(5)

        test.log.info('######## Step 31.Use remote to call DUT - MT voice call.')
        test.expect(test.r1.dstl_voice_call_by_number(test.dut,dut_phone_num))
        test.sleep(20)

        test.log.info('######## Step 32.Check call type. It should be VoLTE. The module still registered to EUTRAN.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*\+COPS: 0,0,\".*\",7.*'))

        test.log.info('######## Step 33.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('at+chup', expect='.*OK.*'))
        test.sleep(5)

        test.log.info('######## Step 34.Config voice domain preference to "IMS PS Voice only".')
        test.expect(test.dut.at1.send_and_verify('at+cevdp=4', expect='.*OK.*'))
        test.sleep(5)
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('at+creg=1', expect='.*OK.*'))
        test.sleep(10)
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_urc('.*\+CREG: 1.*'))
        test.expect(test.dut.at1.send_and_verify('at+cevdp?', expect='\s+\+CEVDP: 4\s+.*OK.*'))
        test.sleep(15)

        test.log.info('######## Step 35.Check IMS voice call availability status.')
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='.*\+CAVIMS: 1.*'))

        test.log.info('######## Step 36.Make MO voice call to remote.')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1,r1_phone_num))
        test.sleep(20)

        test.log.info('######## Step 37.Check call type. It should be VoLTE. The module still registered to EUTRAN.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*\+COPS: 0,0,\".*\",7.*'))

        test.log.info('######## Step 38.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('at+chup', expect='.*OK.*'))
        test.sleep(5)

        test.log.info('######## Step 39.Use remote to call DUT - MT voice call.')
        test.expect(test.r1.dstl_voice_call_by_number(test.dut,dut_phone_num))
        test.sleep(20)

        test.log.info('######## Step 40.Check call type. It should be VoLTE. The module still registered to EUTRAN.')
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*\+COPS: 0,0,\".*\",7.*'))

        test.log.info('######## Step 41.DUT hang up the call.')
        test.expect(test.dut.at1.send_and_verify('at+chup', expect='.*OK.*'))
        test.sleep(5)

    def cleanup(test):
        test.log.info('######## Change to default setting and restart the module.')
        test.expect(test.dut.at1.send_and_verify('at+cevdp=3', expect='.*OK.*'))
        test.expect(test.dut.dstl_restart())


if '__main__' == __name__:
    unicorn.main()
