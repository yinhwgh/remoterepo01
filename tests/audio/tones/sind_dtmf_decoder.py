# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0088243.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_turn_off_emergoff_via_dev_board
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.status_control import configure_event_reporting


class AtSindDtmfDecoder(BaseTest):
    """
    To test Sind Decoder function
    1. 2 modules register to network
    2.set DTMF decoder on DUT side
    3.auxiliary module calls DUT
    4.after call conntect, auxiliary sends some DTMF tones to DUT
    5.DUT can recognise the DTMF tones, and prints DTMF tones by URC
    6.try to send different DTMF tones to DUT
    7.hang up call
    8. set parameters to default values
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_detect(test.r1)
        # dstl_restart(test.dut)
        # dstl_restart(test.r1)
        # test.sleep(10)
        test.log.info('Restore to default configuration')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        pass

    def run(test):
        # for VIPER does not need below 2 steps
        # test.log.info('check at^scfg="Gpio/mode/DAI"')
        # test.expect(test.dut.at1.send_and_verify('at^scfg="Gpio/mode/DAI","std"','.*OK.*'))
        # dstl_restart(test.dut)
        # test.sleep(10)
        test.log.info('Register into network')
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))
        test.log.info('check the SIND')
        test.expect(test.dut.at1.send_and_verify('at^sind?', '.*OK.*'))

        # enable +CIEV URCs for ^SIND for old products:
        test.dut.dstl_configure_common_event_reporting(3, 0, 0, 2)

        test.log.info('set and check sind value')
        test.expect(test.dut.at1.send_and_verify('at^sind="dtmf",0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^sind="dtmf",1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^sind="dtmf",2', '.*OK.*'))
        test.log.info('dut calls r1')
        test.expect(test.dut.at1.send_and_verify('ATD{};'.format(test.r1.sim.nat_voice_nr), '.*OK.*'))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata', '.*OK.*'))
        test.log.info('send dtmf from r1,check the URC in DUT side')
        test.expect(test.r1.at1.send_and_verify('at+vts="1"'))
        test.expect(test.dut.at1.wait_for_strict('\+CIEV: dtmf,"1",1', timeout=5))
        test.expect(test.r1.at1.send_and_verify('at+vts="1"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"1",1', timeout=5))
        test.expect(test.r1.at1.send_and_verify('at+vts="2"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"2",1', timeout=5))
        test.expect(test.r1.at1.send_and_verify('at+vts="3"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"3",1', timeout=5))
        test.expect(test.r1.at1.send_and_verify('at+vts="A"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"A",1', timeout=5))
        test.expect(test.r1.at1.send_and_verify('at+vts="#"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"#",1', timeout=5))
        test.expect(test.dut.at1.send_and_verify('ath', '.*OK.*'))
        pass

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT&W", ".*OK.*"))
        pass


if "__main__" == __name__:
    unicorn.main()
