# author: christian.gosslar@thalesgroup.com
# responsible: christian.gosslar@thalesgroup.com
# location: Berlin

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.phonebook import phonebook_handle
from dstl.auxiliary.init import dstl_detect


import re

# set global PhonBook List, can be adapted later is project has only ME or SM phonebooks
PhoneBookList = [ "ME", "SM"]

class Test(BaseTest):

    def clean_phonbooks(test):
        n=1
        for PB in PhoneBookList:
            test.log.step("Step 0." + str(n) + " clean " + PB + " Phonebook entries")
            test.expect(test.dut.dstl_clear_select_pb_storage(PB))
        return 0

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_collect_module_info_for_mail()

    def run(test):
        """
        Intention:
        Simple check of Phonebook Commands
        Write all entries of the ME and SM Phonebook with max tel length and name length
        """
        # set project depend values
        # PhoneBookList = ["ME", "SM"]
        global PhoneBookList
        if (re.search(test.dut.project, 'JAKARTA')):
            PhoneBookList = ["SM"]

        test.expect(test.dut.dstl_enter_pin())
        test.log.step('Step 0 - enter PIN and clean all Phonebooks ')
        test.clean_phonbooks()

        test.dut.at1.send_and_verify("at+CSCS=\"GSM\"", "OK")
        test.log.step ("Step 1 - write PhoneBook entries into different Phonebooks")
        n=1
        for PhoneBook in PhoneBookList:
            max = test.dut.dstl_get_pb_storage_max_location(PhoneBook)

            test.dut.at1.send_and_verify("at+CPBS=\"" + PhoneBook + "\"")
            test.dut.at1.send_and_verify("at+CPBW=?")
            res = test.dut.at1.last_response
            start_index = res.index(r'CPBW:')
            end_index = res.index(r'OK')
            max_numberlenmgth = res[start_index:end_index].split(',')[1].strip()
            max_namelength = re.sub(".*,", "", res[start_index:end_index]).strip('\r\n')
            # max_namelength = res[start_index:end_index].split(',')[4].strip()
            number = "123456789012345678901234567890123456789012345678901234567890"
            number = number[:int(max_numberlenmgth)]
            name = max_namelength + " Name lenght x2x4x6x8x0x2x4x6x8x0x1x3x5x7x9x"
            name = name[:int(max_namelength)]

            test.log.step ("Step 1." + str(n) + " write into " + PhoneBook + " Phonebook " + str(max) + " entries")
            test.expect(test.dut.dstl_fill_selected_pb_memory(PhoneBook, number=number, text=name))
            n +=1

        test.log.step ("Step 2 - read PhoneBookentries from different Phonebooks")
        n=1
        for PhoneBook in PhoneBookList:
            max = test.dut.dstl_get_pb_storage_max_location(PhoneBook)
            test.log.step ("Step 2." + str(n) + " read from " + PhoneBook + " Phonebook " + str(max) + " entries")
            LastEntry =  "+CPBR: " + str(max) + ","
            test.expect(test.dut.at1.send_and_verify('at+cpbr=1,{}'.format(max), LastEntry))
            n +=1

        test.log.step('Step end')

    def cleanup(test):
        """Cleanup method.
		Nothing to do in this Testcase
        Steps to be executed after test run steps.
        """

        test.log.com('Clean up ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.step('Step x - clean all used Phonebooks ')
        test.clean_phonbooks()
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')


if "__main__" == __name__:
    unicorn.main()
