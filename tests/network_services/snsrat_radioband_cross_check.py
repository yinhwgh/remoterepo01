#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0105148.002


import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.configuration import scfg_radio_band
from dstl.auxiliary import restart_module

class Test(BaseTest):
    '''
    TC0105148.002 - snsrat_radioband_cross_check
    Subscriber :1
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_all_radio_bands()

    def run(test):
        test.log.step('1. Insert sim card to module and restart')
        test.dut.dstl_restart()
        test.log.step('2.Unlock pin, clear band for 3/4G in at^scfg, leave full band for 2G')
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', '.*OK.*'))
        test.dut.dstl_set_radio_band(0, 0, rat='4G')
        test.dut.dstl_set_radio_band(0, rat='3g')

        test.log.step('3.Set preferred rat order to 4G->3G->2G')
        test.expect(test.dut.at1.send_and_verify('AT^SNSRAT=7,2,0', '.*OK.*'))
        test.log.step('4.Register on network by at+cops=0')
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', '.*OK.*'))
        test.log.step('5.verify module should be register on 2G network.')
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT^SMONI', 'SMONI: 2G,'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', 'COPS: 0,.*,.*,0|3'))
        test.log.step('6.Clear bands for all 2/3/4G, '
                      'verify snsrat write command also could be executed.')
        test.expect(test.dut.at1.send_and_verify(' AT^SNSRAT=7,2,0', '.*OK.*'))

    def cleanup(test):
        test.log.step('7. reset to all bands')
        test.dut.dstl_set_all_radio_bands()


if "__main__" == __name__:
    unicorn.main()
