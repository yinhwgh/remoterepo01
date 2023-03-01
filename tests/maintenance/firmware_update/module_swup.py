# responsible: matthias.reissner@thalesgroup.com, christoph.dehm@thalesgroup.com
# location: Berlin
# TC0104817.002, TC0000001.001 

import unicorn
from core.basetest import BaseTest
import os
import subprocess
from dstl.auxiliary import init
from os.path import isfile

os_type = ''


class Test(BaseTest):
    """ module_swup.py
        this script performs one or more times a firmware update by GWinswup.exe or glinswup with a #.USF file

        necessary parameter in device.cfg:
         - swupcmdlineapp=<path_and_application>_C:/temp/gwinswup.exe
         - swupusffile=<path_and_file>_/home/user/swup/PLS83_W_100_120c.usf

        To run this TC in a loop, please use this cmd line parameter:
        --repeat-run=5         # to run only the run() section 5 times in a loop
        example:   unicorn -t tests/maintenance/firmware_update/module_swup.py --repeat-run=50 -l config/bln9_lte083.cfg

        The script aborts if one of the parameter is not defined or the files do not exist.
        NOTE:
            - if the module is used over ASC port, then make sure the correct baudrate is configured and working
            - a baudrate of 460800 with looping 50 times the run() section will take over 13 hours!

        TO DO:
        - take over the baudrate from unicorn device setting - better than hardcoded!
        - receive all outputs from Gwinswup/glinswup tool from stdout AND from stderr
    """

    def setup(test):
        # save original settings from device.cfg as stated in IPIS100333554
        test.dut_at1_original_port_settings = dict(test.dut.at1.settings)

        # check and create path for local firmware file and gwinswup / glinswup binary:
        test.require_parameter('swupcmdlineapp', default='')
        test.bin_file = test.swupcmdlineapp

        test.require_parameter('swupusffile', default='')
        test.usf_file = test.swupusffile

        if test.bin_file is '' or test.usf_file is '':
            test.expect(False, critical=True, msg=f"empty parameter for swup bin or swup usf file: "
                                                  f"'{test.bin_file}','{test.usf_file}'")
        # test.bin_file_name = join(test.bin_file_path, test.swupapp)
        if not isfile(test.bin_file):
            test.expect(False, critical=True, msg=f" Swup application not found. {test.bin_file} - ABORT")
        # test.swup_file_name = join(test.usf_file_path, test.swupusf)
        if not isfile(test.usf_file):
            test.expect(False, critical=True, msg=f" Swup file (*.USF) not found. {test.usf_file} - ABORT")

        test.log.info(f'valid swup-app found: {test.bin_file}')
        test.log.info(f'valid usf-file found: {test.usf_file}')

        # detect Operating System
        # __________________________________________
        if os.sys.platform.startswith('linux'):
            test.os_type = 'LINUX'
            try:
                print("import for Linux")
                # from fcntl import *       # does not work on windows machines in general IMPORT statement
                # but on function level it does not work with import *
                # which one has to be used for Linux ?!?!?!
            except ImportError:
                print("import for Windows")
        # __________________________________________
        elif os.sys.platform.startswith('win'):
            test.os_type = 'WIN'

        else:
            test.expect(False, critical=True, msg=f" could not detect operating system: ({os.sys.platform})")

        test.log.step("Stage 1 Module hard reset")
        test.dut.at1.close()
        test.dut.devboard.open()
        test.sleep(2)
        test.dut.devboard.send_and_verify("mc:vbatt")  # dummy command in case McTest is not responding on first cmd
        test.dut.devboard.send_and_verify("mc:vbatt")
        test.dut.devboard.send_and_verify("mc:vbatt=off")
        test.sleep(10)
        test.dut.devboard.send_and_verify("mc:vbatt=on")
        test.sleep(5)
        test.dut.devboard.send_and_verify("mc:igt=1500")
        test.sleep(30)
        test.dut.dstl_detect()
        test.dut.at1.send_and_verify("at^sqport?")
        test.dut.at1.send_and_verify("ati51")
        pass

    def run(test):
        test.log.step("Stage 2 test_swup")
        ret = -99
        # test.expect(restart_module.dstl_restart(test.dut))
        test.dut.at1.open()
        test.expect(test.dut.at1.send_and_verify("at"))
        test.dut.at1.send_and_verify("ati")
        test.dut.at1.send_and_verify("ati51")
        test.expect(test.dut.at1.send_and_verify("at^cicret=swn"))

        # test.test_cases = []
        # tc = TestCase("Test FW seup", "swup", 12, "glinswup -f=exs82.usf -p=/dev/d2Asc0 -b=460800")
        # test.test_cases.append(tc)

        # current_dir = os.getcwd()
        # test.log.info("Current dir: " + current_dir)

        # with open("/root/jenkins/workspace/Serval_3_ST_pipe/unicorn/result_swup_.xml", "w") as f:
        #    ts = TestSuite("ST auto stage 1", test.test_cases)
        #    TestSuite.to_file(f, [ts], prettyprint = True)
        # test.log.info(TestSuite.to_xml_string([ts]))

        test.log.info("dut port: " + test.dut.at1.port)

        if test.os_type is 'LINUX':
            # # glinswup_path = os.path.join(os.getcwd(), "..", ".." , "..", "glinswup", "glinswup_exs82", "src")
            # # glinswup_exe = os.path.join(os.getcwd(), "..", ".." , "..", "glinswup", "glinswup_exs82", "src", "glinswup_EXS82")
            test.log.info("Swup app: " + test.bin_file)

            # # fw_file_path = os.path.join(os.getcwd(), "..", "fw", "exs82.usf")
            test.log.info("USF file : " + test.usf_file)

            # proc = subprocess.Popen(["glinswup_EXS82", "/dev/" + cdc_dev, "start"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = False)

            # # cg swup
            test.log.info('Running swup cmd: ' + test.bin_file + ' -p=' + test.dut.at1.port + ' -f='
                          + test.usf_file + ' -b=' + str(test.dut_at1_original_port_settings['baudrate']))
            test.dut.at1.close()
            test.sleep(5)
            ret = os.system(test.bin_file + " -p=" + test.dut.at1.port + " -f=" + test.usf_file
                            + " -b=" + str(test.dut_at1_original_port_settings['baudrate']))

        elif test.os_type is 'WIN':
            test.dut.at1.close()
            cmd_line = test.bin_file + " -p:" + test.dut.at1.port + " -f:" + test.usf_file + \
                       " -b:" + str(test.dut_at1_original_port_settings['baudrate'])
            test.log.info(f" >> cmd line execution: {cmd_line}")
            ret = os.system(cmd_line)

        test.log.warning(' ToDo: collect stderr and stdout to catch also errors in case swup fails')
        test.log.info('\n waiting 40 sec for restart of module - serial ports stay detached for this time')
        test.sleep(40)

        test.log.info('  -- ATTENTION! - please wait until module has restarted correct!')
        test.log.info("return: ist " + str(ret) + "<")
        if ret == 0:
            test.log.info("FW Swup successful!")
            test.dut.at1.open()

            # test.dut.at1.close()
            # test.sleep(5)
            # test.dut.at1.open()
            # restart module - test KK 22.09.2021 - start
            '''
            test.dut.devboard.send_and_verify("mc:vbatt")
            test.dut.devboard.send_and_verify("mc:vbatt=off")
            test.sleep(10)
            test.dut.devboard.send_and_verify("mc:vbatt=on")
            test.sleep(5)
            test.dut.devboard.send_and_verify("mc:igt=1500")
            test.sleep(30)
            # restart module - test KK 22.09.2021 - end
            '''

            test.dut.at1.send_and_verify("at")
            test.expect(test.dut.at1.send_and_verify("ati"))
            test.expect(test.dut.at1.send_and_verify("ati51"))
            test.expect(test.dut.at1.send_and_verify("at^cicret=swn"))

        else:
            test.log.warning("FW Swup not successful! " + str(ret))
            test.expect(False)
            test.dut.at1.close()
            test.dut.devboard.send_and_verify("mc:vbatt")  # dummy cmd in case McTest is not responding on first cmd
            test.dut.devboard.send_and_verify("mc:vbatt")
            test.dut.devboard.send_and_verify("mc:vbatt=off")
            test.sleep(10)
            test.dut.devboard.send_and_verify("mc:vbatt=on")
            test.sleep(5)
            test.dut.devboard.send_and_verify("mc:igt=1500")
            test.sleep(25)
            test.dut.at1.open()

        pass

    def cleanup(test):
        test.dut.at1.send_and_verify("ati")
        test.dut.at1.send_and_verify("at^cicret=swn")
        pass


'''   
def syscmd(cmd, encoding=''):
    """
    Runs a command on the system, waits for the command to finish, and then
    returns the text output of the command. If the command produces no text
    output, the command's return code will be returned instead.
    """

    process = subprocess.Popen(
        ["C:/Program Files/GOM/2018/bin/start_gom.exe", "aramis", "-kiosk", "-eval", "gom.script.userscript.test()",
         "Path"], stdout=subprocess.PIPE)
    process.wait()

    p = popen(cmd, Shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
        close_fds=True)
    p.wait()
    output = p.stdout.read()
    if len(output) > 1:
        if encoding:
            return output.decode(encoding)
        else:
            print(output)
            return output
    return p.returncode


p = subprocess.Popen(args)
'''

if "__main__" == __name__:
    unicorn.main()
