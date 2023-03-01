#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0107101.001


import unicorn

from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.configuration import set_autoattach
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.call import setup_voice_call
from dstl.network_service import network_monitor
from dstl.packet_domain import ps_attach_detach
from dstl.network_service import network_access_type

import re

class Test(BaseTest):
    """
    TC0107101.001 - IMSRegistrationControlAndStatus

    Intention:
    UE's voice domain preference can be configured and IMS Voice Call availability
    status can be showed.

    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_network_max_modes()
        test.dut.dstl_enable_ps_autoattach()
        test.dut.dstl_enter_pin()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()

        test.ims_cid, test.ims_init, test.apn_cid, test.apn_init = test.read_initial_pdp_context()
        if not test.ims_cid:
            test.ims_cid = 10
        if not test.apn_cid:
            test.apn_cid = 1
            test.define_pdp_context(test.apn_cid, 'IPV4V6', test.dut.sim.apn_v4)
        test.ims_value = None
        test.dut.at1.send_and_verify("AT+CEVDP=3", "OK")

    def run(test):
        for ims_value in ["1", "0"]:
            test.ims_value = ims_value
            ims_action = "Enable" if test.ims_value == "1" else "Disable"
            test.log.step(f"1.{ims_action} IMS service.")
            test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="MEopMode/IMS","{test.ims_value}"', 'OK'))

            test.pdp_types = ['IPV4V6', 'IPV6', 'IP']
            test.cevdps = [1, 2, 3, 4]

            test.log.info(f"*** Looping steps 2~7  for {test.pdp_types} ***")
            total_loop = len(test.pdp_types)
            current_loop = 0
            for pdp_type in test.pdp_types:
                current_loop += 1
                config_info = f"MEopMode/IMS: {test.ims_value}, loop {current_loop} of {total_loop} -> PDP Type: {pdp_type}"
                test.log.step(f'{config_info} 2. Adding ims context with pdp type {pdp_type}.')
                define_ims = test.define_pdp_context(test.ims_cid, pdp_type, "IMS")
                if not define_ims:
                    test.log.error(f"Fail to define IMS context, skip tests 3~7 for {pdp_type}.")
                    test.output_skipped_steps(begin=3, end=7)
                    continue

                test.log.step(
                    f"{config_info} 3. Reset module and enter pin code, register on 4G network")
                test.dut.dstl_restart()
                test.expect(test.register_to_4G_network())

                test.log.step(f"{config_info} 4. Activate IMS PDP context")
                if test.ims_value == '1':
                    activate_ims = test.activate_ims_pdp_context(manually=False)
                    if not activate_ims:
                        test.log.error(
                            "IMS should be automatically activated when MEopMode/IMS: 1 is set."
                            " To continue tests, activate manually.")
                        activate_ims = test.activate_ims_pdp_context(manually=True)
                else:
                    test.expect(
                        test.dut.at1.send_and_verify('AT+CGACT?', f'CGACT: {test.ims_cid},0'))
                    activate_ims = test.activate_ims_pdp_context(manually=True)

                test.expect(activate_ims,
                                msg=f"Fail to activate IMS context, skip tests 5~7 for {pdp_type}.")
                if not activate_ims:
                    test.output_skipped_steps(begin=5, end=7)
                    continue

                for cevdp in test.cevdps:
                    test.log.step(f"{config_info} 5.Config voice domain preference to {cevdp}")
                    test.dut.at1.send_and_verify(f"AT+CEVDP={cevdp}", "OK")
                    test.sleep(2)

                    test.log.step(
                        f"{config_info} 6.Check IMS voice call availability status with voice domain "
                        f"{cevdp}.")
                    cavims = test.predict_cavims_status(ims_value, cevdp)
                    test.attempt(test.dut.at1.send_and_verify, "AT+CAVIMS?", f"CAVIMS: {cavims}",
                                 retry=3, sleep=1)

                    test.log.step(
                        f"{config_info} 7.Make a voice call(both of MO and MT) with another module and check "
                        f"call type, cevdp: {cevdp}.")
                    for i in range(2):
                        if i < 1:
                            test.log.info(f"****** Setup MO Call, cevdp: {cevdp}******")
                            from_module = test.dut
                            to_module = test.r1
                        else:
                            test.log.info(f"****** Setup MT Call, cevdp: {cevdp}******")
                            from_module = test.r1
                            to_module = test.dut
                        from_module.dstl_voice_call_by_number(to_module, to_module.sim.nat_voice_nr)
                        if cavims == '1':
                            test.log.info("VOLTE call should be setup.")
                            test.expect(test.dut.dstl_monitor_network_act() == '4G')
                        else:
                            test.log.info("Non VOLTE call should be setup.")
                            test.expect(test.dut.dstl_monitor_network_act() in ('2G', '3G'))

                        test.expect(test.dut.dstl_release_call())
                        test.expect(test.r1.dstl_release_call())
                        test.sleep(5)

            test.log.info("Restore CEVPD to 3, so that module is able to register to LTE when IMS is disabled.")
            test.dut.at1.send_and_verify("AT+CEVDP=3", "OK")

    def cleanup(test):
        test.dut.at1.send_and_verify("AT+CEVDP=3", "OK")
        test.log.info("Restore PDP context value.")
        test.dut.dstl_ps_detach()
        if test.ims_init:
            test.dut.at1.send_and_verify(f"AT+CGDCONT={test.ims_init}")
        else:
            test.dut.at1.send_and_verify(f"AT+CGDCONT={test.ims_cid}")
        if test.apn_init:
            test.dut.at1.send_and_verify(f"AT+CGDCONT={test.apn_init}")
        else:
            test.dut.at1.send_and_verify(f"AT+CGDCONT={test.apn_cid}")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","1"', 'OK'))
        test.dut.dstl_restart()

    def read_initial_pdp_context(test):
        """
        Read initial pdp context for LTE and IMS. If non existing context found, return None.
        :return:
        """
        apn_cid = None
        apn_init = None
        ims_cid = None
        ims_init = None

        # read current cids for ims and apn.
        test.dut.dstl_ps_attach()
        test.dut.at1.send_and_verify("AT+CGACT?", "OK")
        activated_cids = re.findall('\+CGACT: (\d+),1', test.dut.at1.last_response)
        test.dut.at1.send_and_verify("AT+CGDCONT?", "OK")
        ims = re.search('(\d+),"(IP.*?)","IMS".*?1,0\s', test.dut.at1.last_response, re.IGNORECASE)
        if ims:
            ims_cid = ims.group(1)
            ims_init = ims.group(0).strip()
            test.log.info(f"Found IMS context id: {ims_cid}.")

        if activated_cids:
            if str(ims_cid) in activated_cids:
                activated_cids.remove(str(ims_cid))
                if activated_cids:
                    apn_cid = activated_cids[0]
                    apn_init = re.findall(f'\+CGDCONT: ({apn_cid},.*?)\s', test.dut.at1.last_response)
                    if apn_init:
                        test.log.info(f"Found PDP context id: {apn_cid}")
                        apn_init = apn_init[0]
        if not apn_cid:
            apn_init = re.findall(f'\+CGDCONT: ((\d+),"IPV4V6","{test.dut.sim.apn_v4}".+)\s+',
                                  test.dut.at1.last_response)
            if apn_init:
                apn_cid = apn_init[0][1]
                apn_init = apn_init[0][0]

        return ims_cid, ims_init, apn_cid, apn_init

    def define_pdp_context(test, cid, ip_type, apn_name):
        test.dut.dstl_ps_detach()
        if apn_name == 'IMS':
            suffix = ',"",0,0,0,0,1,0'
        else:
            suffix = ''
        return test.dut.at1.send_and_verify(f'AT+CGDCONT={cid},"{ip_type}","{apn_name}"{suffix}')

    def predict_cavims_status(test, ims_value, cevdp_value):
        if ims_value == '1' and cevdp_value in [3, 4]:
            test.log.info(f'"MEopMode/IMS" is {ims_value} and cevdp is {cevdp_value}, '
                          f'cavims should be 1.')
            return '1'
        else:
            test.log.info(f'"MEopMode/IMS" is {ims_value} and cevdp is {cevdp_value}, '
                          f'cavims should be 0.')
            return '0'

    def output_skipped_steps(test, begin, end):
        steps = ['3. Reset module and enter pin code, register on 4G network',
                 '4. Activate PDP context',
                 f'5.Config voice domain preference to cevdp {test.cevdps}',
                 '6.Check IMS voice call availability status with voice domain',
                 '7.Make a voice call(both of MO and MT) with another module and check call type']
        for step in steps[begin-3: end-2]:
            test.log.error(f"Skipped step {step}")

    def register_to_4G_network(test):
        test.expect(test.dut.dstl_register_to_network())
        if not test.dut.at1.send_and_verify("AT+COPS?", ".*,7\s+"):
            if not test.dut.at1.send_and_verify("AT+CGATT?", "CGATT: 1"):
                test.dut.dstl_ps_attach()
            if not test.dut.at1.send_and_verify("AT+CGACT?", f"CGACT: {test.apn_cid},1"):
                test.dut.at1.send_and_verify(f"AT+CGACT=1,{test.apn_cid}")
        test.dut.at1.wait_for('C\w?REG: .*,7', timeout=30)
        return test.dut.at1.send_and_verify("AT+COPS?", ".*,7\s+")

    def activate_ims_pdp_context(test, manually=False):
        if not manually:
            activate_ims = test.dut.at1.send_and_verify('AT+CGACT?', f'CGACT: {test.ims_cid},1')
        else:
            activate_ims = test.dut.at1.send_and_verify(f"AT+CGACT=1,{test.ims_cid}", "OK")
            activate_ims &= test.dut.at1.send_and_verify("AT+CGACT?", f"CGACT: {test.ims_cid},1")
        return activate_ims



if __name__ == "__main__":
    unicorn.main()