# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0092923.001
# jira: KRAKEN-535, KRAKEN-741
# feature: LM0004509.010
# prerequisites: dut_at3 has to be configured to UART2/3 as /dev/ttyS1/2 of the modules Linux system!
# description: check modules serial port with simple Linux commands for different baudrates and some text transmission.
#

import unicorn
import time
from core.basetest import BaseTest
import dstl.embedded_system.linux.configuration
from dstl.auxiliary.init import dstl_detect
from dstl.serial_interface import config_baudrate
from dstl.network_service.register_to_network import dstl_register_to_network

testcase_id = "TC0092923.001"
ver = "1.0"


class Test(BaseTest):

    original_baudrate_str = ''
    dut_at3_original_settings = None
    baudrates = {9600, 57600, 230400, 460800, 921600, 115200 }
    # baudrates = {115200 }
    uart_name = '/dev/ttyS1'

    def setup(test):
        test.dut.at1.close()
        test.pin1 = test.dut.sim.pin1
        test.dut.dstl_detect()

        # save original settings from device.cfg of port
        test.dut_at3_original_settings = dict(test.dut.at3.settings)
        # do to problems with EVK 2731 with HW-Flow we have to disable the HW flow on PC side:
        test.dut.at3.reconfigure(settings={"rtscts": False})
        # AND on module side:
        res = test.dut.adb.send_and_receive("stty -F {} -crtscts".format(test.uart_name))
        test.dut.at3.open()
        pass

# -----------------------------------------------------------------------------
# first results with evk2731 in April 2021:
#  - baudrate 460800 does not work well: most characters are corrupt
#  - uart ttyS1 works only in case HW-flow/rtscts is disabled on both sides
#  - uart ttyS2 or others do not work
#
# --> please check on evk2735 also for such settings!
#
# for full findings see:
# https://confluence.gemalto.com/display/IWIKI/Kraken1.0+UARTs#Kraken1.0UARTs-UARTCItestontheMT2731EVK
# and:
# 'Beim MT2735 EVK ist das leider auch so. Das wird sich erst mit dem Kraken-Eval ändern.'
#

    def run(test):
        test.log.info("\n === do TX direction ===")
        for baudrate in test.baudrates:
            test.log.info("\n -------- check baudrate: {} in TX direction ---------".format(baudrate))
            res = test.dut.adb.send_and_receive("stty -F {} {}".format(test.uart_name, baudrate))
            res = test.dut.adb.send_and_receive("stty -F {} -a".format(test.uart_name),
                                                ".*speed {} baud.*".format(baudrate))
            test.dut.at3.reconfigure(settings={"baudrate": baudrate})

            # as Andrzej Trebisz mentioned: port close/open
            test.dut.at3.close()
            test.dut.at3.open()

            test.log.info('>> send some data from module to PC and check it on PC site:')
            test.dut.adb.send_and_receive('echo "Hello from module with baudrate: {}." > /dev/ttyS1'.format(baudrate))
            time.sleep(1)
            ret = test.dut.at3.verify_or_wait_for("Hello from module with baudrate: {}.".format(baudrate), timeout = 3)
            resp = test.dut.at3.last_response
            if ret:
                test.expect(True, 'expected message found - UART works fine.')
            else:
                 test.expect(False, critical=False, msg='expected message NOT found - UART does not work.')
                 test.log.info(' response was: >>' + resp + '<<')

            # flush the input buffer:
            test.dut.at3.read()

            """
            following receive test does not work with Unicorn adb-shell commands
            the cat /dev/ttyS1  or cat /dev/ttyS1 > input.txt  
            is not performed well, neither normal, nor with && sleep 5 at the end.
            Felix assumed to use an app instead of console tools.
            due to other problems with evk2731/35 we have to redesign this UART test
            anyhow after receiving our first KRAKEN_EVFAL modules!


#            test.dut.adb.send_and_receive('ls -la')

            test.log.info("\n === do RX direction ===")
#        for baudrate in test.baudrates:
            test.log.info("\n -------- check baudrate: {} in RX direction ---------".format(baudrate))
#            res = test.dut.adb.send_and_receive("stty -F /dev/ttyS1 {} -crtscts".format(baudrate))
            res = test.dut.adb.send_and_receive("stty -F {} -a".format(test.uart_name), 
                                                ".*speed {} baud.*".format(test.uart_name, baudrate))

#            test.dut.at3.reconfigure(settings={"baudrate": baudrate})
            # as Andrzej Trebisz mentioned: port close/open
#            test.dut.at3.close()
#            test.dut.at3.open()

            test.log.info('>> send some data from PC to module and check it on module site:')

            " " "
            #t1 = test.thread(test.dut.adb.send_and_verify, 'cat {}'.format(test.uart_name)
            #                                      ,'Hello from PC with baudrate: {}.'.format(baudrate) )
            t1 = test.thread(test.dut.adb.send_and_verify, 'cat {} &'.format(test.uart_name), '.*Hello from PC with baudrate: {}.*'.format(baudrate))
            t2 = test.thread(test.dut.at3.send, 'Hello from PC with baudrate: {}.'.format(baudrate))
            t1.join()
            t2.join()
            " " "


            test.dut.adb.send_and_receive('(cat {} >input.txt &) && sleep 3'.format(test.uart_name))

            test.dut.at3.close()
            test.log.info("    freeing port, now you can use CuteCom !!!")

            time.sleep(20)
            # test.dut.at3.send('Hello from PC with baudrate: {}.'.format(baudrate))
            time.sleep(1)
#            test.dut.adb.send_and_receive('ls -la')
            test.dut.adb.send_and_receive('sync')
            test.dut.adb.send_and_receive('ls -la')

            # test.dut.adb.send_and_receive('cat input.txt')


#            ctrl_c =  end="\u001A"
#            test.dut.adb.send_and_receive('\x03')
#            time.sleep(2)

            adb_resp = test.dut.adb.last_response
            print(">>> adb_resp: ", adb_resp)

            test.kill_adb_process('cat {}'.format(test.uart_name))

            " " "
            ret = test.dut.at3.verify_or_wait_for("Hello from PC with baudrate: {}.".format(baudrate), timeout = 3)
            resp = test.dut.at3.last_response
            if ret:
                test.expect(True, 'expected message found - UART works fine.')
            else:
                 test.expect(False, critical=False, msg='expected message NOT found - UART does not work.')
                 test.log.info(' response was: >>' + resp + '<<')
            " " "

            # flush the input buffer:
            test.dut.at3.read()
            """
        pass


    def cleanup(test):
        # set back the device setting to original settings
        """
        reconfigure({
            "baudrate": 115200,
            "timeout": 1,
            "writeTimeout": 0.2,
            "xonxoff": False,
            "rtscts": False,
            "dsrdtr": False,
            "bytesize": 8,
            "stopbits": 1
        })
        """
        test.dut.at3.reconfigure(settings={"baudrate": test.dut_at3_original_settings['baudrate']})
        test.dut.at3.reconfigure(settings={"rtscts": test.dut_at3_original_settings['rtscts']})
        pass


    def kill_adb_process(test, uart_name):
        # res = test.dut.adb.send_and_receive("ps -efa | grep {}".format(uart_name))
        res = test.dut.adb.send_and_receive("ps -efa | grep cat /dev/ttyS1".format(uart_name))
        if "00:00:00 cat " + uart_name in res:
            res_list = res.split()
            ret = test.dut.adb.send_and_receive("kill -9 " + res_list[1])
            res = test.dut.adb.send_and_receive("ps -efa |grep {}".format(uart_name))
        else:
            test.log.info("nothing to kill - process not found!")
        pass


if "__main__" == __name__:
    unicorn.main()

