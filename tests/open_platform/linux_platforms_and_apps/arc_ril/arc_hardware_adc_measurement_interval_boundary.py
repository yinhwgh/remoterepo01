# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0103944.001 arc_hardware_adc_measurement_interval_boundary.py

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
        
        def check_voltage(test, channel=0, value=1000, interval=100, expect=""):
            
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_AdcMeasurement", 
                    "start=1", 
                    "channel={}".format(channel), 
                    "interval={}".format(interval), 
                    "timeout=60", 
                    "exp_adc_measurement={}".format(value)],
                expect=expect,
                expect_exit_code=0)
            
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_AdcMeasurement", 
                    "start=0", 
                    "channel={}".format(channel),
                    "interval=0"],
                expect='',
                expect_exit_code=0) 

        # test.dut.devboard.send_and_verify('MC:ADC1=1000')
        test.dut.dstl_adc_set_voltage(0, 1000)
        
        check_voltage(test, 0, 1000, 100, 'Number of received ADC notifications: [5-6][0-9][0-9]')
        check_voltage(test, 0, 1000, 500, 'Number of received ADC notifications: 1[1-2][0-9]')
        check_voltage(test, 0, 1000, 10000, 'Number of received ADC notifications: [5-7]')
        check_voltage(test, 0, 1000, 30000, 'Number of received ADC notifications: [3-5]')
        
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
