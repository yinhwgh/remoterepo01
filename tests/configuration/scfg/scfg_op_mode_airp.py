#responsible: wen.liu@thalesgroup.com
#location: Dalian
#TC0088026.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.phonebook.phonebook_handle import dstl_set_pb_memory_storage
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode


class Test(BaseTest):
    '''
    TC0088026.001 - TcScfgOpModeAirp
    Intention: This test is provided to verify the functionality of turning on the module (power-up) in Airplane Mode.
    Subscriber: 1
    Note: test was created on McTest
    need add following config in local.cfg file, eg : dut_devboard = dut_usb_devboard and dut_usb_devboard = COM71
    '''


    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.sleep(5)


    def run(test):
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.log.step("1. Write 3 entries into SM phonebook")
        test.expect(test.dut.dstl_enter_pin())
        test.attempt(test.dut.dstl_set_pb_memory_storage, 'SM', retry=5, sleep=2)
        test.expect(test.dut.dstl_write_pb_entries(location=1, number='123456', text='test1'))
        test.expect(test.dut.dstl_write_pb_entries(location=2, number='123456', text='test2'))
        test.expect(test.dut.dstl_write_pb_entries(location=3, number='123456', text='test3'))
        cfun_value = [0, 1, 4]
        m = 1
        n = 1
        test.log.step("1. Set AT^SCFG = MEopMode/CFUN,0")
        test.expect(test.dut.at1.send_and_verify('at^scfg="MEopMode/CFUN",0', expect='OK'))
        for set_cfun in cfun_value:
            test.expect(test.dut.at1.send_and_verify(f'at+cfun={set_cfun}', expect='OK'))
            test.expect(test.dut.dstl_shutdown_smso())
            test.sleep(5)
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board())
            test.dut.at1.wait_for('.*SYSSTART.*')
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify('at+cfun?', expect=f'\+CFUN: {set_cfun}\s+OK'))
            test.expect(test.dut.dstl_enter_pin())
            test.attempt(test.dut.dstl_set_pb_memory_storage, 'SM', retry=5, sleep=2)
            test.expect(test.dut.at1.send_and_verify(f'at+cpbr={m}', expect=f'\+CPBR: {m},"123456",129,"test{m}"\s+OK'))
            m = m+1
        test.log.step("2. Set AT^SCFG = MEopMode/CFUN,1")
        test.expect(test.dut.at1.send_and_verify('at+cfun=1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="MEopMode/CFUN",1', expect='OK'))
        for set_cfun in cfun_value:
            test.expect(test.dut.at1.send_and_verify(f'at+cfun={set_cfun}', expect='OK'))
            test.expect(test.dut.dstl_shutdown_smso())
            test.sleep(5)
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board())
            test.dut.at1.wait_for('.*SYSSTART.*')
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify('at+cfun?', expect=f'\+CFUN: 1\s+OK'))
            test.expect(test.dut.dstl_enter_pin())
            test.attempt(test.dut.dstl_set_pb_memory_storage, 'SM', retry=5, sleep=2)
            test.expect(test.dut.at1.send_and_verify(f'at+cpbr={n}', expect=f'\+CPBR: {n},"123456",129,"test{n}"\s+OK'))
            n = n+1


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('at^scfg="MEopMode/CFUN",1', expect='OK'))
        test.dut.dstl_set_full_functionality_mode()


if '__main__' == __name__:
    unicorn.main()
