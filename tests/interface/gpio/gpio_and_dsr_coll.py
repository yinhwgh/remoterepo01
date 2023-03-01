#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0088192.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.gpio.gpio_on_module import get_gpio_pins_share_state

class Test(BaseTest):
    '''
    TC0088192.001 - GPIOandDSRcoll
    Intention: Testing alternative functionality of GPIO3/DSR line/SPI interface
    Subscriber: 1
    '''
    def setup(test):
        test.dut.dstl_detect()


    def run(test):

        test.log.info('***Test Start***')
        test.log.info('1.Set DSR line by at^scfg as "GPIO"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0","GPIO"','OK'))

        test.log.info('2.Restart module')
        test.dut.dstl_restart()
        test.sleep(10)

        test.log.info('3.Try to configure GPIO3 by at^scpin as output')
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=1', 'OK|ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,2,1', 'OK'))

        test.log.info('4.Try to configure GPIO3 by at^scpin as input')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=0,2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,2,0', 'OK'))

        test.log.info('5.Try to configure DSR line by at cmd. Use every setting of at&s')
        test.expect(test.dut.at1.send_and_verify('AT&S1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT&S0', 'ERROR'))

        if test.dut.dstl_spi_share_asc0_dsr0():
            test.log.info('6.Set SPI by at^scfg as "STD" if supported')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/SPI","std"', 'OK'))
            test.log.info('7.Restart module')
            test.dut.dstl_restart()
            test.sleep(10)
            test.log.info('8.check at^scfg="Gpio/mode/DSR"')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0"', '(?i).*"GPIO/mode/DSR0","rsv".*'))
            test.log.info('9.Set DSR line by at^scfg as "GPIO"')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0","GPIO"', 'OK'))
            test.log.info('10.Restart module')
            test.dut.dstl_restart()
            test.sleep(10)
            test.log.info('11.check at^scfg="Gpio/mode/DSR"')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0"', '(?i).*"GPIO/mode/DSR0","gpio".*'))
            test.log.info('12.check at^scfg="Gpio/mode/SPI"')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/SPI"', '(?i).*"GPIO/mode/SPI","rsv".*'))
        else:
            pass

        test.log.info('13.Set DSR line by at^scfg as "STD"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0","std"', 'OK'))

        test.log.info('14.Restart Module')
        test.dut.dstl_restart()
        test.sleep(10)

        test.log.info('15.check at^scfg="Gpio/mode/DSR"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0"', '(?i).*"GPIO/mode/DSR0","std".*'))

        if test.dut.dstl_spi_share_asc0_dsr0():
            test.log.info('16.check at^scfg="Gpio/mode/SPI"')
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/SPI"', '(?i).*"GPIO/mode/SPI","rsv".*'))
        else:
            pass

        test.log.info('17.Try to configure GPIO3 by at^scpin as output')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,2,1', 'ERROR'))

        test.log.info('18.Try to configure GPIO3 by at^scpin as input')
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=0,2', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT^SCPIN=1,2,0', 'ERROR'))

        test.log.info('19.Configure DSR line by at cmd. Use every setting of at&s')
        test.expect(test.dut.at1.send_and_verify('AT&S1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT&S0', 'OK'))


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT^SPIO=0', 'OK|ERROR'))
        test.log.info('***Test End***')



if "__main__" == __name__:
    unicorn.main()

