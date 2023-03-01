# responsible: michal.kopiel@globallogic.com
# location: Wroclaw
# TC0102592.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_airplane_mode, \
    dstl_is_device_in_airplane_mode
from dstl.configuration.scfg_sms import dstl_scfg_set_sms_auto_acknl, \
    dstl_scfg_get_sms_auto_acknl_mode
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    TC0102592.001   	ScfgSmsAutoAckBasic
    Test intention is to check if  at^scfg="Sms/Autoack" AT-Command
    Description:
    1: Check AT^SCFG=? look for "SMS/AutoAck" acknowledge values.
    2: Check AT^SCFG? command and wait for correct response
    3: Set AT^SCFG="Sms/AutoAck","0" command and wait for correct response
    4a: Check AT^SCFG? stored value
    4b: Check AT^SCFG="SMS/AutoAck" stored value
    5: Set AT^SCFG="Sms/AutoAck","1" command and wait for correct response
    6a: Check AT^SCFG? stored value
    6b: Check AT^SCFG="SMS/AutoAck" stored value
    7: Check again steps 1-6 in Airplane mode
    8: Check if setting is not stored in memory after module restart. On power up this
    functionality is switched off.
    """

    def setup(test):
        dstl_detect(device=test.dut)
        dstl_get_bootloader(device=test.dut)
        dstl_get_imei(device=test.dut)

    def run(test):
        for functionality_level in [1, 4]:
            if functionality_level == 4:
                test.expect(dstl_is_device_in_airplane_mode(device=test.dut))

            test.log.step('Step 1: Check AT^SCFG=? look for "SMS/AutoAck" acknowledge values')
            # 'It command is only for once read - check command syntax for verification supported values'
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=?",
                                                    r'\^SCFG: "SMS/AutoAck",\("0","1"\).*OK.*'))

            test.log.step('Step 2: Check AT^SCFG? command and wait for correct response')
            if functionality_level == 1:
                test.expect(dstl_scfg_get_sms_auto_acknl_mode(device=test.dut,
                                                              get_with_write_command=False) == '0')
            else:
                test.expect(dstl_scfg_get_sms_auto_acknl_mode(device=test.dut,
                                                              get_with_write_command=False) == '1')

            test.log.step('Step 3: Set AT^SCFG="Sms/AutoAck","0" '
                          'command and wait for correct response')
            test.expect(dstl_scfg_set_sms_auto_acknl(device=test.dut, mode=0,
                                                     exp_resp=r'\^SCFG: "SMS/AutoAck","0".*OK.*'))

            test.log.step('Step 4a: Check AT^SCFG? stored value')
            test.expect(dstl_scfg_get_sms_auto_acknl_mode(device=test.dut,
                                                          get_with_write_command=False) == '0')

            test.log.step('Step 4b: Check AT^SCFG="SMS/AutoAck" stored value')
            test.expect(dstl_scfg_get_sms_auto_acknl_mode(device=test.dut,
                                                          get_with_write_command=True) == '0')

            test.log.step('Step  5: Set AT^SCFG="Sms/AutoAck","1" '
                          'command and wait for correct response')
            test.expect(dstl_scfg_set_sms_auto_acknl(device=test.dut, mode=1,
                                                     exp_resp=r'\^SCFG: "SMS/AutoAck","1".*OK.*'))

            test.log.step('Step 6a: Check AT^SCFG? stored value')
            test.expect(dstl_scfg_get_sms_auto_acknl_mode(device=test.dut,
                                                          get_with_write_command=False) == '1')

            test.log.step('Step 6b: Check AT^SCFG="SMS/AutoAck" stored value')
            test.expect(dstl_scfg_get_sms_auto_acknl_mode(device=test.dut,
                                                          get_with_write_command=True) == '1')
            if functionality_level == 1:
                test.log.step('Step 7: Check again steps 1-6 in Airplane mode')
                dstl_set_airplane_mode(device=test.dut)

        test.log.step('Step 8: Check if setting is not stored in memory after module restart. '
                      'On power up this functionality is switched off.')
        test.expect(dstl_restart(device=test.dut))
        test.expect(dstl_scfg_get_sms_auto_acknl_mode(device=test.dut,
                                                      get_with_write_command=False) == '0')
        test.expect(dstl_scfg_get_sms_auto_acknl_mode(device=test.dut,
                                                      get_with_write_command=True) == '0')


def cleanup(test):
    pass


if "__main__" == __name__:
    unicorn.main()
