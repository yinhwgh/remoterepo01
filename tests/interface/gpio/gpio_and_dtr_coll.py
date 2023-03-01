#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0088200.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import switch_to_command_mode
from dstl.gpio.gpio_on_module.close_gpio_driver import dstl_close_gpio_driver


class Test(BaseTest):
    '''
    TC0088200.001 - GPIOandDTRcoll
    Intention: Testing alternative functionality of GPIO1/DTR line
    Subscriber: 1
    '''
    def setup(test):
        test.dut.dstl_detect()


    def run(test):

        test.log.info('***Test Start***')
        test.log.info('1. Set DTR line by at^scfg as "GPIO".')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DTR0","GPIO"', 'OK'))

        test.log.info('2. Restart module.')
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_register_to_network()
        test.sleep(5)

        test.log.info('3. Try to configure AT&D with every available parameter.')
        test.expect(test.dut.at1.send_and_verify('AT&D0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT&D1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT&D2', 'ERROR'))

        test.log.info('4. Configure GPIO1 by at^scpin as output to high and disable.')
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,0,1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=0,0', 'OK'))

        test.log.info('5. Configure GPIO1 by at^scpin as output to low and disable.')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,0,1,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=0,0', 'OK'))

        test.log.info('6. Configure GPIO1 by at^scpin as input and disable.')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,0,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=0,0', 'OK'))

        test.log.info('7.*Establish data connection (PPP)')
        test.expect(test.dut.at1.send_and_verify('atd*99#', 'CONNECT', wait_for='CONNECT'))
        test.sleep(1)

        test.log.info('8. *Toggle DTR line')
        test.dut.at1.connection.setDTR(True)
        test.sleep(1)
        test.dut.at1.connection.setDTR(False)
        test.sleep(1)
        test.dut.at1.connection.setDTR(True)
        test.sleep(1)

        test.log.info('9. *Release data connection(PPP).')
        test.dut.dstl_switch_to_command_mode_by_pluses()

        test.log.info('10. * Return to data mode.')
        test.expect(test.dut.at1.send_and_verify('ato', 'CONNECT', wait_for='CONNECT'))
        test.sleep(1)

        test.log.info('11. *Abort connection.')
        test.dut.dstl_switch_to_command_mode_by_pluses()

        test.log.info('12. Configure GPIO1 by at^scpin as output to LOW state and disable.')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,0,1,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=0,0', 'OK'))

        test.log.info('13. Set DTR line by at^scfg as "STD".')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DTR0","std"', 'OK'))

        test.log.info('14. Restart Module.')
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_register_to_network()
        test.sleep(5)

        test.log.info('15. Try to configure GPIO1 by at^scpin as output.')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,0,1', 'ERROR'))

        test.log.info('16. Try to configure GPIO1 by at^scpin as input.')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,0,0', 'ERROR'))

        test.log.info('17. Set at&d0.')
        test.expect(test.dut.at1.send_and_verify('AT&D0', 'OK'))

        test.log.info('18. *Establish data connection (PPP).')
        test.expect(test.dut.at1.send_and_verify('atd*99#', 'CONNECT', wait_for='CONNECT'))
        test.sleep(1)

        test.log.info('19. *Toggle DTR line')
        test.dut.at1.connection.setDTR(True)
        test.sleep(1)
        test.dut.at1.connection.setDTR(False)
        test.sleep(1)
        test.dut.at1.connection.setDTR(True)
        test.sleep(1)

        test.log.info('20. *Release data connection.')
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())

        test.log.info('21. *Return to data mode.')
        test.expect(test.dut.at1.send_and_verify('ato', 'CONNECT', wait_for='CONNECT'))
        test.sleep(1)

        test.log.info('22. *Abort connection.')
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.sleep(5)

        test.log.info('23. Set at&d1')
        test.expect(test.dut.at1.send_and_verify('AT&D1', 'OK'))

        test.log.info('24. *Establish data connection (PPP)')
        test.expect(test.dut.at1.send_and_verify('atd*99#', 'CONNECT', wait_for='CONNECT'))
        test.sleep(1)

        test.log.info('25. *Toggle DTR line')
        test.dut.at1.connection.setDTR(True)
        test.sleep(1)
        test.dut.at1.connection.setDTR(False)
        test.sleep(1)
        test.dut.at1.connection.setDTR(True)
        test.sleep(1)

        test.log.info('26. *Return to data mode.')
        test.expect(test.dut.at1.send_and_verify('ato', 'CONNECT', wait_for='CONNECT'))
        test.sleep(1)

        test.log.info('27. *Abort connection.')
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.sleep(10)

        test.log.info('28. Set at&d2.')
        test.expect(test.dut.at1.send_and_verify('AT&D2', 'OK'))

        test.log.info('29. *Establish data connection (PPP).')
        test.expect(test.dut.at1.send_and_verify('atd*99#', 'CONNECT', wait_for='CONNECT'))
        test.sleep(1)

        test.log.info('30. *Toggle DTR line.')
        test.dut.at1.connection.setDTR(True)
        test.sleep(1)
        test.dut.at1.connection.setDTR(False)
        test.sleep(1)
        test.dut.at1.connection.setDTR(True)
        test.sleep(1)
        test.expect(test.dut.at1.wait_for('NO CARRIER'))

    def cleanup(test):
       test.log.info('***Test End***')
       test.dut.dstl_close_gpio_driver()



if "__main__" == __name__:
    unicorn.main()

