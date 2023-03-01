# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096523.001 arc_hardware_adc_measurement_all_channels.py

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
        
        def check_voltage(test, channel=0, value=100):
            
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_AdcMeasurement", 
                    "start=1", 
                    "channel={}".format(channel), 
                    "interval=1000", 
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

        
        channels = []
        if 'MC' in test.dut.devboard.version:
            test.log.warning('MC-Test in use. Only two channels can be checked!')
            channels = [0, 1]
        elif 'DSB2016' in test.dut.devboard.version:
            test.log.info('DSB2016 in use. Checking four channels.')
            channels = [0, 1, 3, 4]
        
        test.log.step('Checking voltage 1700mV')
        for c in channels:
            test.dut.dstl_adc_set_voltage(c, 1700)
            # 'SOUR:DAC1 1700'
            # 'SOUR:DAC2 1700'
            # 'SOUR:DAC4 1700'
            # 'SOUR:DAC5 1700'              
            
        for c in channels:
            check_voltage(test, c, value=1700)             

        
        test.log.step('Checking voltage 100mV')
        for c in channels:
            test.dut.dstl_adc_set_voltage(c, 100)
            # 'SOUR:DAC1 100'
            # 'SOUR:DAC2 100'
            # 'SOUR:DAC4 100'
            # 'SOUR:DAC5 100'     

        for c in channels:
            check_voltage(test, c, value=100) 

        for c in channels:
            test.dut.dstl_adc_set_voltage(c, 0)
            # 'SOUR:DAC1 0'
            # 'SOUR:DAC2 0'
            # 'SOUR:DAC4 0'
            # 'SOUR:DAC5 0' 
            
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions('external')


if "__main__" == __name__:
    unicorn.main()
