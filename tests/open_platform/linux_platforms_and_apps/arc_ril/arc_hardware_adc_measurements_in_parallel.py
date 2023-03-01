# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096524.001 arc_hardware_adc_measurements_in_parallel.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard.devboard import dstl_ignite_module
from dstl.auxiliary.devboard.devboard import dstl_get_dev_board_version
from dstl.auxiliary.devboard.adc_on_devboard import dstl_adc_set_voltage
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        test.expect(test.dut.devboard, critical=True)
        test.dut.dstl_get_dev_board_version()
        
    def run(test):
        
        def check_voltage(test, channel=0, value=100, interval=1000):
            
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_AdcMeasurement", 
                    "start=1", 
                    "channel={}".format(channel), 
                    "interval={}".format(interval), 
                    "timeout=60", 
                    "exp_adc_measurement={}".format(value)],
                expect='EXP',
                expect_exit_code=0)
            
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_AdcMeasurement", 
                    "start=0", 
                    "channel={}".format(channel),
                    "interval=0"],
                expect='stopped',
                expect_exit_code=0) 

        def check_voltage_single_loop(test, channel, value):
            for i in range(10):
                check_voltage(test, channel=channel, value=value)
                test.sleep(2)

        def check_voltage_sequence(test, channel, value):
            check_voltage(test, channel=channel, value=value, interval=1000)


        # test.dut.devboard.send_and_verify('MC:ADC1=100')
        # test.dut.devboard.send_and_verify('MC:ADC2=100')
        test.dut.dstl_adc_set_voltage(0, 100)
        test.dut.dstl_adc_set_voltage(1, 100)
        t1 = test.thread(check_voltage_single_loop, test, 1, 100)
        t2 = test.thread(check_voltage_sequence, test, 0, 100)
        t1.join()
        t2.join()
        
        
        # test.dut.devboard.send_and_verify('MC:ADC1=1000')
        # test.dut.devboard.send_and_verify('MC:ADC2=1000')
        test.dut.dstl_adc_set_voltage(0, 1000)
        test.dut.dstl_adc_set_voltage(1, 1000)        
        t1 = test.thread(check_voltage_single_loop, test, 1, 1000)
        t2 = test.thread(check_voltage_sequence, test, 0, 1000)
        t1.join()
        t2.join()

        # test.dut.devboard.send_and_verify('MC:ADC1=1700')
        # test.dut.devboard.send_and_verify('MC:ADC2=1700')
        test.dut.dstl_adc_set_voltage(0, 1700)
        test.dut.dstl_adc_set_voltage(1, 1700)
        t1 = test.thread(check_voltage_single_loop, test, 1, 1700)
        t2 = test.thread(check_voltage_sequence, test, 0, 1700)
        t1.join()
        t2.join()


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
