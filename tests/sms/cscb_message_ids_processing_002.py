#responsible: sebastian.lupkowski@globallogic.com
#location: Wroclaw
#TC0093291.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """
    It shall be possible to add or delete MIDs(Cell Broadcast Message ID specification) within a specified range of MIDS
     without any problems.
    After adding or deleting of MIDS ranges the program checks if resulting number of ranges is possible to further
    processing. If not, ERROR should be returned.
    Additional info:
    On some DUTs there is an AT Command AT^SCFG=SMS/CB,<0|1> which allows enabling and disabling of cell broadcast
    support for 3GPP access technologies.
    Some DUTs may require that it is not allowed to delete/modify specific cell broadcast messages ID (eg. presidential
    alert 4370 for Bobcat ALAS66A-W)

    1. If AT^SCFG="SMS/CB"is supported on DUT check if cell broadcast functionality is enabled (AT^SCFG="SMS/CB","1").
    If not supported this point should be omitted!!!
    2. Delete all configured cell broadcast message identifiers (CBM IDs) - AT+CSCB=1
    3. Check if all MIDs have been deleted - AT+CSCB?
    4. Define maximum quantity of CBM single IDs
    5. Check if all MIDs have been added - AT+CSCB?
    6. Define quantity of CBM single IDs higher than maximum
    7. Check if all MIDs remained as in step 5 - AT+CSCB?
    8. Delete all configured cell broadcast message identifiers (CBM IDs) - AT+CSCB=1
    9. Check if all MIDs have been deleted - AT+CSCB?
    10. Define maximum quantity of CBM ranged IDs
    11. Check if all MIDs have been added - AT+CSCB?
    12. Define quantity of CBM ranged IDs higher than maximum
    13. Check if all MIDs remained as in step 11 - AT+CSCB?
    14. Delete all configured cell broadcast message identifiers (CBM IDs) - AT+CSCB=1
    15. Check if all MIDs have been deleted - AT+CSCB?
    16. Define maximum quantity of CBM ranged and single IDs combined
    17. Check if all MIDs have been added - AT+CSCB?
    18. Define quantity of CBM ranged and single IDs combined higher than maximum
    19. Check if all MIDs remained as in step 17 - AT+CSCB?
    20. Delete all configured cell broadcast message identifiers (CBM IDs) - AT+CSCB=1
    21. Check if all MIDs have been deleted - AT+CSCB?
    """
    cmd_ok = ".*OK.*"
    cmd_cms_error = ".*\+CMS ERROR: .*"
    query_command = "AT+CSCB?"
    delete_command = "AT+CSCB=1"
    write_command = "AT+CSCB=0"
    max_qty_single_ids = '2,4,6,8,10,13,16,19,22,25,28,31,34,37,40,43,46,49'
    over_max_qty_single_ids = '2,4,6,8,10,13,16,19,22,25,28,31,34,37,40,43,46,49,52'
    max_qty_ranged_ids = '0-1,12-13,30-31,48-49,66-67,84-85,102-103,126-127'
    over_max_qty_ranged_ids = '0-1,12-13,30-31,48-49,66-67,84-85,102-103,126-127,150-151'
    max_qty_combined_ids = '0-2,4,6,8,10,12-13,16,19,22,30-31,48-49,66-67'
    over_max_qty_combined_ids = '0-2,4,6,8,10,12-13,16,19,22,25,28,30-31,48-49,66-67'
    empty_response = '.*\+CSCB: 1,"","".*OK.*'


    def setup(test):
        test.log.h2("Starting TP for TC0093291.002 - CscbMessageIDsProcessing")
        test.log.info("Preparing module")
        test.prepare_module()

    def run(test):
        test.log.step('1. If AT^SCFG="SMS/CB"is supported on DUT check if cell broadcast functionality is enabled '
                      '(AT^SCFG="SMS/CB","1").If not supported this point should be omitted!!!')
        test.dut.at1.send_and_verify('AT^SCFG?', test.cmd_ok)
        if '"SMS/CB","1"' in test.dut.at1.last_response:
            test.log.info("CB functionality enabled")
        elif '"SMS/CB","0"' in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="SMS/CB","1"', test.cmd_ok))
        else:
            test.log.info('AT^SCFG="SMS/CB" not supported - step omitted')

        test.log.step('2. Delete all configured cell broadcast message identifiers (CBM IDs) - AT+CSCB=1')
        test.expect(test.dut.at1.send_and_verify(test.delete_command, test.cmd_ok))

        test.log.step('3. Check if all MIDs have been deleted - AT+CSCB?')
        test.expect(test.dut.at1.send_and_verify(test.query_command, test.empty_response))

        test.log.step('4. Define maximum quantity of CBM single IDs')
        test.expect(test.dut.at1.send_and_verify(f'{test.write_command},"{test.max_qty_single_ids}"', test.cmd_ok))

        test.log.step('5. Check if all MIDs have been added - AT+CSCB?')
        test.expect(test.dut.at1.send_and_verify(test.query_command, f'\+CSCB: 0,"{test.max_qty_single_ids}",""'))

        test.log.step('6. Define quantity of CBM single IDs higher than maximum')
        test.expect(test.dut.at1.send_and_verify(f'{test.write_command},"{test.over_max_qty_single_ids}"', test.cmd_cms_error))

        test.log.step('7. Check if all MIDs remained as in step 5 - AT+CSCB?')
        test.expect(test.dut.at1.send_and_verify(test.query_command, f'\+CSCB: 0,"{test.max_qty_single_ids}",""'))

        test.log.step('8. Delete all configured cell broadcast message identifiers (CBM IDs) - AT+CSCB=1')
        test.expect(test.dut.at1.send_and_verify(test.delete_command, test.cmd_ok))

        test.log.step('9. Check if all MIDs have been deleted - AT+CSCB?')
        test.expect(test.dut.at1.send_and_verify(test.query_command, test.empty_response))

        test.log.step('10. Define maximum quantity of CBM ranged IDs')
        test.expect(test.dut.at1.send_and_verify(f'{test.write_command},"{test.max_qty_ranged_ids}"', test.cmd_ok))

        test.log.step('11. Check if all MIDs have been added - AT+CSCB?')
        test.expect(test.dut.at1.send_and_verify(test.query_command, f'\+CSCB: 0,"{test.max_qty_ranged_ids}",""'))

        test.log.step('12. Define quantity of CBM ranged IDs higher than maximum')
        test.expect(test.dut.at1.send_and_verify(f'{test.write_command},"{test.over_max_qty_ranged_ids}"', test.cmd_cms_error))

        test.log.step('13. Check if all MIDs remained as in step 11 - AT+CSCB?')
        test.expect(test.dut.at1.send_and_verify(test.query_command, f'\+CSCB: 0,"{test.max_qty_ranged_ids}",""'))

        test.log.step('14. Delete all configured cell broadcast message identifiers (CBM IDs) - AT+CSCB=1')
        test.expect(test.dut.at1.send_and_verify(test.delete_command, test.cmd_ok))

        test.log.step('15. Check if all MIDs have been deleted - AT+CSCB?')
        test.expect(test.dut.at1.send_and_verify(test.query_command, test.empty_response))

        test.log.step('16. Define maximum quantity of CBM ranged and single IDs combined')
        test.expect(test.dut.at1.send_and_verify(f'{test.write_command},"{test.max_qty_combined_ids}"', test.cmd_ok))

        test.log.step('17. Check if all MIDs have been added - AT+CSCB?')
        test.expect(test.dut.at1.send_and_verify(test.query_command, f'\+CSCB: 0,"{test.max_qty_combined_ids}",""'))

        test.log.step('18. Define quantity of CBM ranged and single IDs combined higher than maximum')
        test.expect(test.dut.at1.send_and_verify(f'{test.write_command},"{test.over_max_qty_combined_ids}"', test.cmd_cms_error))

        test.log.step('19. Check if all MIDs remained as in step 17 - AT+CSCB?')
        test.expect(test.dut.at1.send_and_verify(test.query_command, f'\+CSCB: 0,"{test.max_qty_combined_ids}",""'))

        test.log.step('20. Delete all configured cell broadcast message identifiers (CBM IDs) - AT+CSCB=1')
        test.expect(test.dut.at1.send_and_verify(test.delete_command, test.cmd_ok))

        test.log.step('21. Check if all MIDs have been deleted - AT+CSCB?')
        test.expect(test.dut.at1.send_and_verify(test.query_command, test.empty_response))

    def cleanup(test):
        test.dut.at1.send_and_verify("AT&F", test.cmd_ok)
        test.dut.at1.send_and_verify("AT&W", test.cmd_ok)

    def prepare_module(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", test.cmd_ok))


if "__main__" == __name__:
    unicorn.main()