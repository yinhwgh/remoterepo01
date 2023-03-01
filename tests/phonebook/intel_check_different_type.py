# responsible: yandong.wu@thalesgroup.com;xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0087931.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.phonebook import phonebook_handle
import re


class Test(BaseTest):
    '''
        TC0087931.001 - IntelCheckDifferentType
        Intention: Write entries with different types to the selected phonebook.
                   <br />129 ISDN / telephony numbering plan, national / international unknown
                   <br />145 ISDN / telephony numbering plan, international number
                   <br />128 &#8211; 255 Other values refer TS 24.008 section 10.5.4.7
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))

    def run(test):
        test.r1_int_num = test.r1.sim.int_voice_nr
        test.r1_nat_num = test.r1.sim.nat_voice_nr
        pb_mem = ['ON', 'FD', 'SM']
        type_mo = ['129', '145', '161']
        for mem in pb_mem:
            for test_type in type_mo:
                test.log.info(f'***Start test PB memory {mem} with type {test_type}***')
                test.check_pb_diff_type(mem, test_type)
                test.log.info(f'***End test PB memory {mem} with type {test_type}***')

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))

    def check_pb_diff_type(test, pb_memory, type_n):
        if type_n == '145':
            write_number = test.r1_int_num
            read_number = '\\' + test.r1_int_num
        elif type_n == '129':
            write_number = test.r1_int_num
            read_number = test.r1_int_num.strip('\+')
        else:
            write_number = test.r1_nat_num
            read_number = test.r1_nat_num
        test.log.step('1.set phonebook memory,check how many entries are possible')
        index_max = test.dut.dstl_get_pb_storage_max_location(pb_memory)
        test.log.step('2.write all entries into the selected phonebook and read each written entry')
        for i in range(1, index_max + 1):
            test.expect(test.dut.dstl_write_pb_entries(i, write_number, type_n, str(i)))
            test.expect(test.dut.at1.send_and_verify(f'at+cpbr={i}',
                                                     f'CPBR: {i},"{read_number}",{type_n},"{str(i)}"'))
        test.log.step('3.try to write one more entry into the selected phonebook than allowed')
        test.expect(test.dut.dstl_write_pb_entries(index_max + 1, write_number, type_n,
                                                   str(index_max + 1)) == False)
        test.log.step('4.check how many phonebook entries are supported (AT+CPBR=?)')
        test.expect(test.dut.at1.send_and_verify('at+cpbr=?', f'\+CPBR: \(1-{index_max}\)'))
        test.log.step('5.read selected phonebook (AT+CPBR=1, x)')
        test.expect(test.dut.at1.send_and_verify(f'at+cpbr=1,{index_max}', 'OK'))
        cpbr_response = test.dut.at1.last_response
        for i in range(1, index_max + 1):
            if re.search(f'\+CPBR: {i},"{read_number}",{type_n}', cpbr_response):
                continue
            else:
                test.expect(False)
                test.log.error(f'PB index {i} not displayed correct, please check!')

        test.log.step('6.delete all entries with AT+CPBW command')
        test.expect(test.dut.dstl_clear_select_pb_storage(pb_memory))


if '__main__' == __name__:
    unicorn.main()
