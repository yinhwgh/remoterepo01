#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0105090.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.usim.get_imsi import dstl_get_imsi

class Test(BaseTest):
    """
    TC0105090.001	SindPacspFunctionCheck
    Debuged:Viper
    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_get_imsi()
        test.expect(test.dut.dstl_lock_sim())
        test.dut.dstl_enter_pin()
        return


    def run(test):
        test.log.step(
            '1.Update EF_CSP(6F15) content to "C080FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF".')
        test.update_efcsp('C080FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        test.log.step(
            '2.Restart moudle without enter pin1,then request the presentation mode and current value of "pacsp"')
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.check_pacsp_value(0,99)
        test.log.step('3.Verify pin,then request the presentation mode and current value of "pacsp"')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.check_pacsp_value(0, 1)
        test.log.step(
            '4.Update EF_CSP(6F15) content to "C000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF".')
        test.update_efcsp('C000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        test.log.step(
            '5.Restart moudle without enter pin1,then request the presentation mode and current value of "pacsp"')
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.check_pacsp_value(0, 99)
        test.log.step('6.Verify pin,then request the presentation mode and current value of "pacsp"')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.check_pacsp_value(0, 0)
        test.log.step(
            '7.Update EF_CSP(6F15) content to "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF".')
        test.update_efcsp('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        test.log.step(
            '8.Restart moudle without enter pin1,then request the presentation mode and current value of "pacsp"')
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.check_pacsp_value(0, 99)
        test.log.step('9.Verify pin,then request the presentation mode and current value of "pacsp"')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.check_pacsp_value(0, 99)

        test.log.step('10.Enable "pacsp" indicator,then request the presentation mode and current value of "pacsp"')
        test.expect(test.dut.at1.send_and_verify('at^sind="pacsp",1', 'OK'))
        test.check_pacsp_value(1, 99)
        test.log.step('11.Update EF_CSP(6F15) content to "C080FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF".')
        test.update_efcsp('C080FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        test.log.step('12.Send refresh proactive command to DUT,check URC.')
        test.refresh_efcsp(True,1)
        test.log.step('13.Request the presentation mode and current value of "pacsp"')
        test.check_pacsp_value(1, 1)
        test.log.step('14.Update EF_CSP(6F15) content to "C000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF".')
        test.update_efcsp('C000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        test.log.step('15.Send refresh proactive command to DUT,check URC.')
        test.refresh_efcsp(True,0)
        test.log.step('16.Update EF_CSP(6F15) content to "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC080".')
        test.update_efcsp('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC080')
        test.log.step('17.Send refresh proactive command to DUT,check URC.')
        test.refresh_efcsp(True,1)
        test.log.step('18.Update EF_CSP(6F15) content to "C080FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF".')
        test.update_efcsp('C080FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        test.log.step('19.Send refresh proactive command to DUT,check URC.')
        test.refresh_efcsp(False)
        
        test.log.step('20.Disable "pacsp" indicator,then request the presentation mode and current value of "pacsp"')
        test.expect(test.dut.at1.send_and_verify('at^sind="pacsp",0', 'OK'))
        test.check_pacsp_value(0, 1)
        test.log.step('21.Update EF_CSP(6F15) content to "C000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF".')
        test.update_efcsp('C000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        test.log.step('22.Send refresh proactive command to DUT,check URC.')
        test.refresh_efcsp(False)
        test.log.step('23.Request the presentation mode and current value of "pacsp"')
        test.check_pacsp_value(0, 0)
        test.log.step('24.Update EF_CSP(6F15) content to "C080FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF".')
        test.update_efcsp('C080FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        test.log.step('25.Send refresh proactive command to DUT,check URC.')
        test.refresh_efcsp(False)
        test.log.step('26.Request the presentation mode and current value of "pacsp"')
        test.check_pacsp_value(0, 1)

    def cleanup(test):
        pass

    def check_pacsp_value(test,expect_mode,expect_value):
        test.expect(test.dut.at1.send_and_verify('AT^SIND?', 'OK'))
        response = re.search(r'SIND: pacsp,(\d),(\d+)', test.dut.at1.last_response)
        mode_1 = int(response.group(1))
        init_value_1=int(response.group(2))

        test.expect(test.dut.at1.send_and_verify('AT^SIND="pacsp",2', 'OK'))
        response = re.search(r'SIND: pacsp,(\d),(\d+)', test.dut.at1.last_response)
        mode_2 = int(response.group(1))
        init_value_2=int(response.group(2))
        if mode_1 != expect_mode or mode_2 != expect_mode or init_value_1 != expect_value or init_value_2 != expect_value:
            test.log.error('pacsp in sind response is wrong,mode should be {},initValue should be {}'.format(expect_mode,expect_value))
        else:
            test.log.info('pacsp in sind response is ok')

    def update_efcsp(test,content):
        if len(content) !=36:
            test.log.error('Only support updating 18 bytes data currently.')
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004027FFF"', '.*\+CSIM: 4,"61\w\w".*OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004026F15"', '.*\+CSIM: 4,"61\w\w".*OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=46,"00D6000012{}"'.format(content), '.*\+CSIM: 4,"9000".*OK'))

    def refresh_efcsp(test,is_urc_popup,ind_value=99):
        test.expect(test.dut.at1.send_and_verify('at^sstk="D0128103010102820281829207013F007FFF6F15"', 'OK'))
        test.sleep(10)
        if is_urc_popup:
           if test.dut.at1.wait_for('+CIEV: pacsp,{}'.format(ind_value)):
               return True
           else:
               test.log.error('URC should popup after refresh')
        else:
            if test.dut.at1.wait_for('+CIEV: pacsp,{}'.format(ind_value),timeout=90):
                test.log.error('URC should not popup after refresh')
            else:
                return True



if "__main__" == __name__:
    unicorn.main()