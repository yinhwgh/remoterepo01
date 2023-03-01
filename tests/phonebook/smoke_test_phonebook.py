# responsible: michal.kopiel@globallogic.com
# location: Wroclaw
# TC0095496.002

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.phonebook.phonebook_handle import dstl_set_pb_memory_storage, dstl_write_pb_entries, \
    dstl_read_pb_entry, dstl_delete_pb_entry, dstl_get_pb_storage_max_location, \
    dstl_clear_select_pb_storage
from dstl.security.unlock_sim_pin2 import dstl_enter_pin2


class Test(BaseTest):
    """
    The test will do the following checks with the phonebooks: SM, ME, ON and FD.
    1. Fill the phonebook with 3 entries on each phonebook memory storage.
    2. Read the phonebook.
    3. Remove entries from phonebook.
    4. Read the phonebook.
    """

    def setup(test):
        test.voice_national_number = test.dut.sim.nat_voice_nr

        dstl_detect(device=test.dut)
        dstl_get_imei(device=test.dut)
        test.expect(dstl_enter_pin(device=test.dut))
        test.expect(dstl_enter_pin2(device=test.dut))
        test.sleep(5)

    def run(test):
        phonebooks = ['SM', 'ME', 'ON', 'FD']

        for phonebook in phonebooks:
            max_range = 4
            test.log.info(f'=== Loop for phonebook: {phonebook} ===')
            test.expect(dstl_set_pb_memory_storage(device=test.dut, storage=phonebook))
            storage_capacity = test.expect(
                dstl_get_pb_storage_max_location(device=test.dut, storage=phonebook))
            test.expect(dstl_clear_select_pb_storage(device=test.dut, storage=phonebook))

            test.log.step('1. Fill the phonebook with 3 entries on each phonebook memory storage.')
            test.log.info(f'Phonebook capacity: {storage_capacity}')
            if (storage_capacity < 3):
                max_range = (storage_capacity + 1)
                test.log.info(f'the number of entries will be made according to the'
                              f' max phonebook location: {storage_capacity}')
            for entry in range(1, max_range):
                test.expect(dstl_write_pb_entries(device=test.dut, location=entry,
                                                  number=test.voice_national_number,
                                                  type='129', text=f'test_dut_{entry}'))

            test.log.step('2. Read the phonebook.')
            for entry in range(1, max_range):
                test.expect(dstl_read_pb_entry(device=test.dut, location=entry,
                                               number=test.voice_national_number,
                                               type='129', text=f'test_dut_{entry}'))

            test.log.step('3. Remove entries from phonebook.')
            for entry in range(1, max_range):
                test.expect(dstl_delete_pb_entry(device=test.dut, location=entry))

            test.log.step('4. Read the phonebook.')
            for entry in range(1, max_range):
                test.expect(not dstl_read_pb_entry(device=test.dut, location=entry,
                                                   number=test.dut.sim.nat_voice_nr,
                                                   type='129', text=f'test_dut_{entry}'))

    def cleanup(test):
        test.expect(dstl_set_pb_memory_storage(device=test.dut, storage='SM'))


if "__main__" == __name__:
    unicorn.main()
