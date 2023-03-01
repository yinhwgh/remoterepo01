# responsible: michal.kopiel@globallogic.com
# location: Wroclaw
# TC0010461.001, TC0010461.002

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.configure_sms_text_mode_parameters import \
    dstl_get_supported_sms_event_reporting_configuration, dstl_configure_sms_event_reporting
from dstl.sms.configure_sms_text_mode_parameters import dstl_read_sms_event_reporting_configuration
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    TC0010461.001 / TC0010461.002    Csms

    To test the behavior of new SMS message indications (at+cnmi) depending
     on phase2 and phase2+ features.
    Test should be performed in 3GPP networks.
    Network providers support short message service.
    One module is used and has to be attached to network.

    Step 1 Check parameters of at+cnmi command which are supported in phase2 (at+csms=0)
    Step 2 Test at+cnmi command and use not supported parameters (e.g. mt=2/3 and ds=1)
    to provoke errors
    Step 3 Check parameters of cnmi-command which are supported in phase2+ (at+csms=1)
    Step 4 Test at+cnmi command with the same parameters again, no error shall occur
    Step 5 Switch back to phase2 and the error message will appear.
    """

    PHASE_2 = "0"
    PHASE_2_PLUS = "1"
    OK = ".*OK.*"
    ERROR = ".*ERROR.*"

    def setup(test):
        dstl_detect(device=test.dut)
        dstl_get_bootloader(device=test.dut)
        dstl_get_imei(device=test.dut)
        test.expect(dstl_register_to_network(device=test.dut))
        test.expect(dstl_set_error_message_format(device=test.dut, err_mode="2"))
        test.expect(dstl_set_character_set(device=test.dut, character_set='GSM'))
        test.expect(dstl_select_sms_message_format(device=test.dut))
        test.expect(dstl_set_preferred_sms_memory(device=test.dut, preferred_storage='ME'))
        test.expect(dstl_delete_all_sms_messages(device=test.dut))

    def run(test):
        test.log.step(
            "Step 1 Check parameters of at+cnmi command which are supported in phase2 (at+csms=0)")
        test.expect(dstl_configure_sms_event_reporting(device=test.dut, mode='0', mt='0',
                                                       bm='0', ds='0', bfr='1'))
        test.expect(dstl_set_message_service(device=test.dut, service=test.PHASE_2))
        test.set_and_check_cnmi_settings(phase=test.PHASE_2, exp_resp=test.OK)

        test.log.step(
            "Step 2 Test at+cnmi command and use not supported parameters (e.g. mt=2/3 and ds=1) "
            "to provoke errors")
        test.set_and_check_cnmi_settings(phase=test.PHASE_2, exp_resp=test.ERROR)

        test.log.step(
            "Step 3 Check parameters of cnmi-command which are supported in phase2+ (at+csms=1)")
        test.expect(dstl_set_message_service(device=test.dut, service=test.PHASE_2_PLUS,
                                             exp_resp=test.OK))
        test.set_and_check_cnmi_settings(phase=test.PHASE_2_PLUS, exp_resp=test.OK)

        test.log.step(
            "Step 4 Test at+cnmi command with the same parameters again, no error shall occur")
        test.set_and_check_cnmi_settings(phase=test.PHASE_2_PLUS, exp_resp=test.OK)

        test.log.step("Step 5 Switch back to phase2 and the error message will appear.")
        test.set_and_check_cnmi_settings(phase=test.PHASE_2, exp_resp=test.ERROR, step_5=True)

    def cleanup(test):
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(device=test.dut))

    def set_and_check_cnmi_settings(test, phase, exp_resp, step_5=False):
        status, cnmi_response, _ = dstl_get_supported_sms_event_reporting_configuration(test.dut)
        if status:
            mode_parameters = cnmi_response.mode
            bfr_parameters = cnmi_response.bfr
            bm_parameters = cnmi_response.bm

        if phase == test.PHASE_2 and exp_resp == test.OK:
            mt_parameters = ["0", "1"]
            ds_parameters = ["0"]
        elif phase == test.PHASE_2 and exp_resp == test.ERROR:
            mt_parameters = ["2", "3"]
            ds_parameters = ["1"]
            if step_5:
                exp_resp = test.OK
        else:
            mt_parameters = ["0", "1", "2", "3"]
            ds_parameters = ["0", "1"]

        if status == True:
            for mode in mode_parameters:
                for mt in mt_parameters:
                    for bm in bm_parameters:
                        for ds in ds_parameters:
                            for bfr in bfr_parameters:
                                test.expect(dstl_configure_sms_event_reporting(
                                    device=test.dut, mode=mode, mt=mt, bm=bm, ds=ds, bfr=bfr,
                                    exp_resp=exp_resp))

                                if exp_resp == ".*OK.*":
                                    test.expect(
                                        dstl_read_sms_event_reporting_configuration(
                                            device=test.dut) == {"mode": f'{mode}', "mt": f'{mt}',
                                                                 "bm": f'{bm}', "ds": f'{ds}',
                                                                 "bfr": f'{bfr}'})
                                    if step_5:
                                        test.expect(dstl_set_message_service(
                                            device=test.dut, service=test.PHASE_2,
                                            exp_resp=test.ERROR))
                                else:
                                    test.expect(
                                        dstl_read_sms_event_reporting_configuration(device=test.dut)
                                        == {"mode": '0', "mt": '0', "bm": '0',
                                            "ds": '0', "bfr": '1'})
        else:
            test.expect(value=False, critical=True,
                        msg="impossible to get supported values - test impossible to execution")
        test.log.info("Restore CNMI Factory values")
        test.expect(dstl_configure_sms_event_reporting(device=test.dut, mode='0', mt='0',
                                                       bm='0', ds='0', bfr='1'))


if "__main__" == __name__:
    unicorn.main()
