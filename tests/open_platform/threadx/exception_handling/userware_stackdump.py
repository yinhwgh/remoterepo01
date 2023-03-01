# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0107226.001 uw_stackdump
# jira: SRV04-217, SRV04-42
# feature:
# docu: https://confluence.gemalto.com/display/IWIKI/Serval4.0+New+AT+Commands

import unicorn
import os
from core.basetest import BaseTest
import dstl.embedded_system.embedded_system_configuration
from dstl.auxiliary.init import dstl_detect
from dstl.miscellaneous.ffs_properties import dstl_get_ffs_disks
from dstl.miscellaneous.access_ffs_by_at_command import dstl_clear_directory, dstl_list_directory, dstl_read_status
from dstl.miscellaneous.read_ffs_file_binary import dstl_read_ffs_file_binary
from dstl.auxiliary.devboard.devboard import dstl_switch_off_at_echo, dstl_switch_on_at_echo


class Test(BaseTest):
    appname = ''
    dst_test_path = ''
    logPath = ''
    osSep = ''

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')

        test.logPath = test.workspace
        print("logPath:", test.logPath)
        test.osSep = os.sep

        # Workaround for missing dut_log interface - now it is prerequisite for validation PCs
        # if test.dut.log is not None:
        # test.dut.log.open()     # channel for debug output

        test.dut.dstl_detect()
        # disabling ECHO function on McTest to have a better readable log file:
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        test.dut.dstl_switch_off_at_echo(serial_ifc=1)

        test.appname = 'exception.bin'
        ret, err_msg = test.dut.dstl_install_app(test.appname)
        if not ret:
            test.expect(False, critical=True, msg=err_msg)

        # restart not needed here: test.dut.dstl_restart()

        # switch to +CMEE:1 to see the numeric error code and store setting:
        test.expect(test.dut.at1.send_and_verify("at+CMEE=1"))
        # test.expect(test.dut.at1.send_and_verify("at&w"))

        # set and check settings before all starts
        test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/URC,ON'))     # necessary for this test
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?"))

        dst_drive = test.dut.dstl_get_ffs_disks()[0]
        dst_drive = dst_drive.replace('"', '')  # test.text_src_file_path
        test.dst_test_path = dst_drive.rstrip('/')
        test.dst_test_path = test.dst_test_path + "/backtrace/"

        list_dir = test.dut.dstl_list_directory(dst_drive)
        if 'backtrace/' in list_dir:
            test.dut.dstl_clear_directory(test.dst_test_path)
            test.expect(test.dut.at1.send_and_verify('at^sfsa="rmdir","{}"'.format(test.dst_test_path),   # + '/')
                                                     '(?s).*SFSA: 0.*OK'))

        list_dir = test.dut.dstl_list_directory(dst_drive + '/')
        if 'backtrace/' in list_dir:
            test.expect(
                test.expect(False, msg="sub folder backtrace still existst - should not!")
            )
        pass

    def run(test):
        """
        Intention:
        Check SDK Example exception.bin. It runs into same exception handling and creates subfolder .\backtrace
        and puts there some stackdump files into.
        This test checks if this folder and files are created and how big they are
        Prerequisites: the app exception.bin from SDK examples
        """

        loglevel = "0"
        test.log.step('\n_______Step 1: Start app and check both UART interfaces for correct output')
        # set output channel to different one than current (Serval needs this):
        # test.dut.dstl_set_uw_trace_interface()  # does not work on it's own IF number!
        # ret, ifnum = test.dut.dstl_get_sqport("at1")
        # test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum, device_interface="at2"))
        # test.expect(test.dut.at2.send_and_verify('at^scfg=userware/trace/level,{}'.format(loglevel)))

        test.dut.dstl_start_app(test.appname, device_interface="at2")

        # wait for last output:
        test.expect(test.dut.at2.wait_for_strict(
            'Too much APP exceptions - hold and unload APP completely', timeout=55))

        test.sleep(1)
        test.expect(test.dut.at2.send_and_verify("at+CMEE=1"))
        """
        in case module is not accessible anymore after a crash, restart it by this sequence:
            test.dut.dstl_turn_off_vbatt_via_dev_board()
            test.dut.dstl_turn_on_vbatt_via_dev_board()
            test.dut.dstl_turn_on_igt_via_dev_board(time_to_sleep=2)
            time.sleep(5)
        """
        state, running_app = test.dut.dstl_get_running_app()
        if running_app is not "":
            test.expect(False, msg="running app found, but there should not be a running app anymore!")

        list_dir = test.dut.dstl_list_directory(test.dst_test_path)
        print('files from path: ' + test.dst_test_path)
        print(list_dir)

        freadcontent = b''
        freadsize = 0

        stackdump_size = 0
        for list_name in list_dir:
            # test.text_src_file_name_abs = join(test.text_src_file_path, test.text_src_file_name)
            status_values = test.dut.dstl_read_status(test.dst_test_path + list_name)
            print('file size of', list_name, 'is', status_values['fileSize'])
            stackdump_size += int(status_values['fileSize'])

            freadhandle = test.dut.dstl_open_file(test.dst_test_path + list_name, 64, )
            if freadhandle is not False:
                freadsize, freadcontent = test.dut.dstl_read_ffs_file_binary(freadhandle, status_values['fileSize'])
                ret = _file_writer(test.logPath + test.osSep + list_name, freadcontent)

            test.expect(test.dut.dstl_close_file(freadhandle))

        print('file size of stackdump is', stackdump_size)
        if stackdump_size < 16400:
            test.expect(False, msg="Stackdump size has to be over 16400 bytes - it is not, it is: {}"
                        .format(stackdump_size))

        pass

    def cleanup(test):
        """Cleanup method.
        disable Userware/Autostart otherwise bad influence to following tests
        """

        ret = test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at1")
        if not ret:
            test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at2")
        elif not ret:
            test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at3")

        # switch back to default user profile settings:
        test.expect(test.dut.at1.send_and_verify("at&f"))
        test.expect(test.dut.at1.send_and_verify("at&w"))

        # set back to disabled autostart and disabled output interface
        test.expect(test.dut.dstl_set_uw_autostart_state(state='0'))

        # enable ECHO function on McTest:
        test.dut.dstl_switch_on_at_echo(serial_ifc=0)

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass


def _file_writer(path, content):
    file_object = open(path, 'wb')
    try:
        ret = file_object.write(content)
    finally:
        file_object.close()
    return ret


if "__main__" == __name__:
    unicorn.main()
