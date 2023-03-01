#responsible: michal.jastrzebski@globallogic.com
#location: Wroclaw
#TC0092206.002

import unicorn
import datetime
import random
from time import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin



class Test(BaseTest):
    """
    Check that low transition at GPIO “EMERG_RST” restarts the module during voice call.

    1. Power on modules, and send AT command to both modules
    2. Check that both modules are logged in to the network using at+creg command
    3. Establish voice connection between modules from Subscriber_1 to Subscriber_2.
    4. Connect Subscriber_1 EMERG_RST pin with the ground pin on DSB75
    5. Check on Subscriber_2 that connection is hung up, check if NO CARRIER appears.
    6. Try to Send AT command to Subscriber_1 module.
    7. Disconnect Subscriber_1 EMERG_RST pin with the ground pin on DSB75
    8. Establish voice connection between modules from Subscriber_1 to Subscriber_2.
    9.Check that Subscriber_1 module is working, sending AT command.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):

        test.log.info('1. Power on modules, and send AT command to both modules.')
        test.expect(test.dut.at1.send_and_verify('ATI', 'OK'))
        test.expect(test.r1.at1.send_and_verify('ATI', 'OK'))

        test.log.info('2. Check that both modules are logged in to the network using at+creg command.')
        test.expect(test.dut.at1.send_and_verify('at+creg=1', expect='.*OK.*'))
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*\+CREG: 1,1.*'))
        test.expect(test.r1.at1.send_and_verify('at+creg=1', expect='.*OK.*'))
        test.expect(test.r1.dstl_enter_pin())
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*\+CREG: 1,1.*'))

        test.log.info('3. Establish voice connection between modules from Subscriber_1 to Subscriber_2.')
        test.expect(test.dut.at1.send_and_verify('ATD{};'.format(test.r1.sim.nat_voice_nr), '.*OK.*'))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ATA', '.*OK.*'))

        test.log.info('4. Connect Subscriber_1 EMERG_RST pin with the ground pin on DSB75 or Mctest.')
        test.expect(test.dut.devboard.send_and_verify('mc:emergoff=1', 'OK'))

        test.log.info('5. Check on Subscriber_2 that connection is hung up, check if NO CARRIER appears.')
        test.r1.at1.send('AT', end="\r\n")
        test.sleep(4)
        test.expect('.*NO CARRIER.*' not in test.r1.at1.read())

        test.log.info('6. Try to Send AT command to Subscriber_1 module.')
        test.dut.at1.send('AT', end="\r\n")
        test.sleep(1)
        test.expect('.*OK.*' not in test.dut.at1.read())

        test.log.info('7. Disconnect Subscriber_1 EMERG_RST pin with the ground pin on DSB75 or McTest.')
        test.expect(test.dut.devboard.send_and_verify('mc:emergoff=0', 'OK'))
        test.expect(test.r1.at1.send_and_verify('AT+CHUP', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))
        test.sleep(5)

        test.log.info('8. Establish voice connection between modules from Subscriber_1 to Subscriber_2.')
        test.expect(test.dut.at1.send_and_verify('at+creg=1', expect='.*OK.*'))
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*\+CREG: 1,1.*'))
        test.expect(test.dut.at1.send_and_verify('ATD{};'.format(test.r1.sim.nat_voice_nr), '.*OK.*'))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ATA', '.*OK.*'))

        test.log.info('9. Check that Subscriber_1 module is working, sending AT command.')
        test.expect(test.dut.at1.send_and_verify('ATI', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG?', 'OK'))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', '.*OK.*'))

if "__main__" == __name__:
    unicorn.main()
