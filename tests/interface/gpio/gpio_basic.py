# responsible: @thalesgroup.com
# author: christoph.dehm@thalesgroup.com
# location: Dalian
# TC0105514.001 - AtSpio_Basic

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.devboard.gpio_on_devboard import dstl_set_gpio_direction_for_all, dstl_set_gpio_direction
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    TC0105514.001 - AtSpio_Basic
    Intention: test AT^SPIO if GPIOs are useable in INPUT and OUTPUT direction and
                their signals are verified/created by McTestv4
                AT^SCPOL or AT^SGPINCA or AT^SGPICFG are not part of this test
    Subscriber: 1
    McTest: McTest v4/extension necessary
    """
    report = ''

    def setup(test):
        test.dut.dstl_detect()

        # this is important to set the correct GPIO-setting
        if test.dut.project is 'SERVAL':
            test.dut.devboard.send_and_verify('MC:MODULE=EXS82')
        elif test.dut.project is 'VIPER':
            test.dut.devboard.send_and_verify('MC:MODULE=PLS83')

        test.dut.dstl_set_gpio_direction_for_all("IN")

        # test.dut.dstl_set_gpio_direction_for_all("OUT")
        # test.dut.devboard.send_and_verify('mc:gpiocfg?')
        # test.dut.dstl_set_gpio_direction_for_all("IN")
        test.dut.devboard.send_and_verify('mc:gpiocfg?')
        # test._disable_gpios()
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=0', '(OK|\+CME ERROR: 767|\+CME ERROR: operation failed)'))
        pass

    def run(test):
        at_scpin_test_resp = '- - - undefined - - -'
        if test.dut.project is 'SERVAL':
            gpios_all = {6, 7, 21, 21, 22, 23}  # all known GPIOs of the product
            gpios_others = {25}                 # not possible with McTest
            at_scpin_test_resp = '\^SCPIN: \(0-1\),\(6,7,20-23,25\),\(0-1\),\(0-1\)\s+OK'
            at_sgio_test_resp = '\^SGIO: \(6,7,20-23,25\)\s+OK'
            at_ssio_test_resp = '\^SSIO: \(6,7,20-23,25\),\(0,1\)\s+OK'

        elif test.dut.project is 'VIPER':
            gpios_all = {4,              # FastShutdown
                         5,              # Status LED
                         6, 7, 8,        #
                         11, 12, 13, 14, 15,    # SDC1
                         16, 17, 18, 19, # ASC1 + SPI
                         20, 21         # DOUT, DIN
                         }
            gpios_others = {1, 2, 3,     # ASC0 signals
                            24, 25, 26}      # not possible with McTest
            at_scpin_test_resp = '\^SCPIN: \(0-1\),\(0-7,10-20,23-25\),\(0-1\),\(0-1\)\s+OK'
            at_sgio_test_resp = '\^SGIO: \(0-7,10-20,23-25\)\s+OK'
            at_ssio_test_resp = '\^SSIO: \(0-7,10-20,23-25\),\(0,1\)\s+OK'

        else:
            test.expect(False, critical=True, msg="Project not found - please adapt script to project!")

        test.log.info('*** Test Start ***')

        test.log.step(' 1. check for illegal usage of at-cmds')
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=0', '(OK|\+CME ERROR: 767|\+CME ERROR: operation failed)'))
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=2', 'CME ERROR: '))
        test.expect(test.dut.at1.send_and_verify('AT^SPIO?', 'CME ERROR: '))
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=', 'CME ERROR: '))

        test.log.step(' 2. check functionality of SCPIN, SGIO and SSIO')
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=?', '\^SPIO: \(0-1\)\s+OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=?', at_scpin_test_resp))
        test.expect(test.dut.at1.send_and_verify('AT^SGIO=?', at_sgio_test_resp))
        test.expect(test.dut.at1.send_and_verify('AT^SSIO=?', at_ssio_test_resp))

        # set gpio mode on shared lines:
        test._set_gpio_mode_settings('gpio')    # performs restart to take effect!

        # disable ASC1 on McTest to keep hands off from serial signal lines
        test.dut.devboard.send_and_verify('mc:asc1=OFF')

        test.expect(test.dut.at1.send_and_verify('AT^SPIO=1'))
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=1', '\+CME ERROR: (767|operation failed)'))

        test.log.info('-------------------------------------------------------')
        test.log.h2('set all GPIOs to out and low/high - verify with devboard')
        for gpio in gpios_all:
            test.log.info('-------------------------------------------------------')
            test.log.h3(f' test GPIO {gpio} as output with high and low:')
            # test.dut.dstl_set_gpio_direction(gpio, 'IN')  # devboard, already done in setup()
            ret = test._set_gpio_dir(gpio, 'OUT', 'HIGH')
            if True:   # ret:
                direction, value = test.dut.dstl_get_gpio_state(test._mct(gpio))
                test.log.info(f'dstl_get_gpio_state() returned for gpio{gpio} - dir: {direction}, value: {value}')
                if value is not '1':
                    test.dut.devboard.send_and_verify('mc:gpiocfg?')
                    msg = f'\n GPIO{gpio} fails as output high signal'
                    test.expect(False, msg=msg)
                    test.report += msg
                else:
                    test.expect(True)

                test._set_gpio_state(gpio, 'LOW')
                direction, value = test.dut.dstl_get_gpio_state(test._mct(gpio))
                test.log.info(f'dstl_get_gpio_state() returned for gpio{gpio} - dir: {direction}, value: {value}')
                if value is not '0':
                    test.dut.devboard.send_and_verify('mc:gpiocfg?')
                    msg = f'\n GPIO{gpio} fails as output low  signal'
                    test.expect(False, msg=msg)
                    test.report += msg
                else:
                    test.expect(True)

            else:
                test.log.warning('setting has failed: it does not make sense to test the GPIO pin: overjump it')

        test.report += '\n'

        test.log.h2('set all GPIOs to in - verify with devboard')
        for gpio in gpios_all:
            test.log.info('-------------------------------------------------------')
            test.log.h3(f' test GPIO {gpio} as input with high and low:')
            test.expect(test.dut.at1.send_and_verify(f'AT^SCPIN=0,{test._gpio_no(gpio)}'))
            # test.dut.dstl_set_gpio_direction(gpio, 'IN')  # devboard, already done in setup()
            ret = test._set_gpio_dir(gpio, 'IN')
            if ret:
                test.dut.dstl_set_gpio_direction(test._mct(gpio), 'out')
                test.dut.dstl_set_gpio_state(test._mct(gpio), '1')
                ret = test.expect(test.dut.at1.send_and_verify(f'AT^SGIO={test._gpio_no(gpio)}', '\^SGIO: 1\s+OK.*'))
                if not ret:
                    test.dut.devboard.send_and_verify('mc:gpiocfg?')
                    test.report += f'\n GPIO{gpio} fails as input high signal'

                test.dut.dstl_set_gpio_state(test._mct(gpio), '0')
                ret = test.expect(test.dut.at1.send_and_verify(f'AT^SGIO={test._gpio_no(gpio)}', '\^SGIO: 0\s+OK.*'))
                if not ret:
                    test.dut.devboard.send_and_verify('mc:gpiocfg?')
                    test.report += f'\n GPIO{gpio} fails as input low signal'
                    test.sleep(5)
                    ret = test.expect(
                        test.dut.at1.send_and_verify(f'AT^SGIO={test._gpio_no(gpio)}', '\^SGIO: 1\s+OK.*'))

            else:
                test.log.warning('setting has failed: it does not make sense to test the GPIO pin: overjump it')
            # set the output pin back to input on McT, otherwise bad influence possible, i.E. module restart!
            test.dut.dstl_set_gpio_direction(test._mct(gpio), 'in')

        pass

    def cleanup(test):
        # set all GPIO lines back to input of McTest:
        test.dut.dstl_set_gpio_direction_for_all("IN")
        # enable ASC1 on McTest
        test.dut.devboard.send_and_verify('mc:asc1=atmap')

        test.dut.devboard.send_and_verify('mc:gpiocfg?')


        # disable GPIO setting of the module:
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=0'))
        test._set_gpio_mode_settings('std')

        if test.report is '':
            test.log.info(' REPORT: no error found!')
        else:
            test.log.error(f'   REPORT:\n{test.report}\n')

        test.log.info('***Test End***')
        pass

    def _disable_gpios(test, ):
        for gpio in range(1, 10, 1):
            test.expect(test.dut.at1.send_and_verify(f'AT^scpin=0,{test._gpio_no(gpio)}'))
        return

    def _set_gpio_dir(test, gpio, dir='', startvalue=''):
        """
            sets a modules GPIO line to in/out
        :param gpio:    pin number
        :param dir:     in/out
        :param startvalue: if out, then this can be used to set high=1/low=0
        :return:
        """
        my_gpio = test._gpio_no(gpio)

        if 'IN' in dir:
            return test.expect(test.dut.at1.send_and_verify(f'AT^scpin=1,{my_gpio},0'))
        elif 'OUT' in dir:
            if startvalue is '':
                return test.expect(test.dut.at1.send_and_verify(f'AT^scpin=1,{my_gpio},1'))
            else:
                if startvalue is 0 or 'LOW' in startvalue.upper():
                    return test.expect(test.dut.at1.send_and_verify(f'AT^scpin=1,{my_gpio},1,0'))
                elif startvalue is 1 or 'HIGH' in startvalue.upper():
                    return test.expect(test.dut.at1.send_and_verify(f'AT^scpin=1,{my_gpio},1,1'))
                else:
                    test.expect(False, msg=f"_set_gpio_dir() with unknown value for startvalue: {startvalue}")

        else:
            test.expect(False, msg=f"_set_gpio_dir() with unknown value for dir: {dir}")
        return False

    def _set_gpio_state(test, gpio, state):
        """
            sets a modules GPIO line signal to hi/low
        :param gpio:    pin number
        :param state:   high/1 or low/0
        :return:
        """
        my_gpio = test._gpio_no(gpio)

        if state is 0 or 'LOW' in state.upper():
            return test.expect(test.dut.at1.send_and_verify(f'AT^ssio={my_gpio},0'))
        elif state is 1 or 'HIGH' in state.upper():
            return test.expect(test.dut.at1.send_and_verify(f'AT^ssio={my_gpio},1'))

        test.expect(False, msg=f"_set_gpio_state() with unknown value for state: {state}")
        return False

    def _mct(self, gpio):
        return gpio - 1

    def _gpio_no(test, gpio):
        if 'VIPER' is test.dut.project:     # to be compatible with GINGER
            return gpio - 1                 # Jakarta, Ginger and Viper are counting GPIO1..10 as <pin_id> 0..9
        else:
            return gpio                     # all other take GPIO1..10 as <pin_id> 1..10

    def _set_gpio_mode_settings(test, value):
        if 'VIPER' is test.dut.project:
            test.dut.at1.send_and_verify(f'AT^SCFG=GPIO/Mode/ASC1,{value}')     # 16, 17, 18, 19
            test.dut.at1.send_and_verify(f'AT^SCFG=GPIO/Mode/RING0,{value}')    # 24
            test.dut.at1.send_and_verify(f'AT^SCFG=GPIO/Mode/DAI,{value}')      # 20, 21
            # test.dut.at1.send_and_verify(f'AT^SCFG=GPIO/Mode/FNS,{value}')    # 26  - SIM dual mode
            test.dut.at1.send_and_verify(f'AT^SCFG=GPIO/Mode/FSR,{value}')      # 4 - fast shutdown
            # test.dut.at1.send_and_verify(f'AT^SCFG=GPIO/Mode/MCLK,{value}')    # master clock signal
            test.dut.at1.send_and_verify(f'AT^SCFG=GPIO/Mode/SYNC,{value}')     # 5 - LED status
            test.log.step(" restarting module to take effect of new SCFG=GPIO settings:")
            test.expect(test.dut.dstl_restart())
            test.sleep(9)
            test.expect(test.dut.at1.send_and_verify('AT^SCFG?'))
        return


if "__main__" == __name__:
    unicorn.main()
