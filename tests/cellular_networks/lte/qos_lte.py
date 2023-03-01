# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0088059.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
import re


class Test(BaseTest):
    '''
    TC0088059.001 - QoSLte
    Intention: Ensure, that is possible to configure different profiles of quality of service for 4th generation networks
    Subscriber: 1
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_register_to_lte()
        test.apn = test.dut.sim.gprs_apn
        test.apn2 = test.dut.sim.gprs_apn_2
        test.log.info('***Test Start***')

    def run(test):
        cid = 4
        test.log.info('1.define 1 additional possible PDP context(cid=4)')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.set_pdp_context(cid, test.apn)

        test.log.info('2.try to set several illegal LTE QoS profiles')
        max_dl_gbr_value, max_ul_gbr_value, max_dl_mbr_value, max_ul_mbr_value = test.get_max_qos_parameter()

        test.invalid_param_test('17')
        test.invalid_param_test('1,10')
        test.invalid_param_test('2,1,-1')
        test.invalid_param_test('3,2,' + str(int(max_dl_gbr_value) + 1))
        test.invalid_param_test('4,4,0,-1')
        test.invalid_param_test('5,1,10' + str(int(max_ul_gbr_value) + 1))
        test.invalid_param_test('6,3,100,5000,-1')
        test.invalid_param_test('1,5,1000,50' + str(int(max_dl_mbr_value) + 1))
        test.invalid_param_test('1,2,10000,5000,101,-1')
        test.invalid_param_test('1,2,10000,50,101,' + str(int(max_ul_mbr_value) + 1))

        test.log.info('3.test several valid LTE QoS profiles as follows for guaranteed bit rate - QCI=1-4')

        for i in range(1, 5):
            test.log.info(f'Start Test QCI value: {i}')
            test.log.info('3.1 set and check the LTE QoS profiles with minimum acceptable parameters')
            test.set_qos_param(cid, i, '0,0,0,0')

            test.step2to3(cid, 3)

            test.log.info('3.4. set the minimum acceptable LTE QoS profile to maximum values')
            test.set_qos_param(cid, i,
                               f'{max_dl_gbr_value}, {max_ul_gbr_value}, {max_dl_mbr_value}, {max_ul_mbr_value}')

            test.log.info('3.5. repeat steps 3.2. and 3.3')
            test.step2to3(cid, 3)

            test.log.info('3.6. set LTE QoS profile to requested values of parameters')
            test.set_qos_param(cid, i, '10000,5000,10000,5000')

            test.log.info('3.7. repeat steps 3.2. and 3.3')
            test.step2to3(cid, 3)

            test.log.info(f'End Test QCI value: {i}')

        test.log.info(
            '4.test several valid LTE QoS profiles as follows for non-guaranteed bit rate and QCI selected by the network - QCI=5-9,0')
        for i in [5, 6, 7, 8, 9, 0]:
            test.log.info(f'Start Test QCI value: {i}')

            test.log.info('4.1. set and check the LTE QoS profiles without additionally parameters')
            test.set_qos_param(cid, i)
            test.expect(test.dut.at1.send_and_verify('AT+CGEQOS?', f'.*CGEQOS: {cid},{i}.*.*OK.*'))

            test.step2to3(cid, 4)

            test.log.info(f'End Test QCI value: {i}')

    def cleanup(test):
        test.log.info('***Test End***')

    def set_pdp_context(test, cid, apn):
        test.expect(test.dut.at1.send_and_verify(f'at+cgdcont={cid},"IP","{apn}"', 'OK'))

    def get_max_qos_parameter(test):
        test.dut.at1.send_and_verify('at+cgeqos=?', 'OK')
        res = test.dut.at1.last_response
        pattern = '.*CGEQOS: .*,.*,\\(0-(\d+)\\),\\(0-(\d+)\\),\\(0-(\d+)\\),\\(0-(\d+)\\).*'

        max_dl_gbr = re.search(pattern, res).group(1)
        max_ul_gbr = re.search(pattern, res).group(2)
        max_dl_mbr = re.search(pattern, res).group(3)
        max_ul_mbr = re.search(pattern, res).group(4)

        test.log.info('Max DL GBR: {}\n Max UL GBR: {}\n Max DL MBR: {}\n Max UL MBR: {}'.format(max_dl_gbr, max_ul_gbr,
                                                                                                 max_dl_mbr,
                                                                                                 max_ul_mbr))
        return max_dl_gbr, max_ul_gbr, max_dl_mbr, max_ul_mbr

    def invalid_param_test(test, params):
        test.expect(test.dut.at1.send_and_verify(f'at+cgeqos={params}', 'ERROR'))

    def set_qos_param(test, cid, qci, params=''):
        if params:
            test.expect(test.dut.at1.send_and_verify(f'at+cgeqos={cid},{qci},{params}', 'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify(f'at+cgeqos={cid},{qci}', 'OK'))

    def step2to3(test, cid, step):
        int_r1_phone_num = test.r1.sim.int_voice_nr
        if test.dut.project == 'VIPER':
            test.log.info(f'{step}.2. activate the related PDP context and check AT+CGCONTRDP and AT+CGEQOSRDP')
            test.expect(test.dut.at1.send_and_verify(f'at+cgact=1,{cid}', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},1'))
            test.expect(test.dut.at1.send_and_verify(f'atd{int_r1_phone_num};', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+CGEQOSRDP', '.*CGEQOSRDP: \d+,\d+,\d+,\d+,\d+,\d+.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('ath', 'OK'))

            test.log.info(f'{step}.3. deactivate the active PDP context and check AT+CGCONTRDP and AT+CGEQOSRDP')
            test.expect(test.dut.at1.send_and_verify(f'at+cgact=0,{cid}', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},0'))
            test.expect(test.dut.at1.send_and_verify(f'atd{int_r1_phone_num};', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+CGEQOSRDP', '.*CGEQOSRDP: \d+,\d+,\d+,\d+,\d+,\d+.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('ath', 'OK'))
        else:
            test.log.info(f'{step}.2. activate the related PDP context and check AT+CGCONTRDP and AT+CGEQOSRDP')
            test.expect(test.dut.at1.send_and_verify(f'at+cgact=1,{cid}', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},1'))
            test.expect(test.dut.at1.send_and_verify(f'at+CGCONTRDP={cid}', '.*CGCONTRDP: 4,([5-9]),.*'))
            test.expect(test.dut.at1.send_and_verify('at+CGEQOSRDP', '.*CGEQOSRDP: 4.*OK'))

            test.log.info(f'{step}.3. deactivate the active PDP context and check AT+CGCONTRDP and AT+CGEQOSRDP')
            test.expect(test.dut.at1.send_and_verify(f'at+cgact=0,{cid}', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},0'))
            test.expect(test.dut.at1.send_and_verify(f'at+CGCONTRDP={cid}', '.*CGCONTRDP: 4,([5-9]),.*'))
            test.expect(test.dut.at1.send_and_verify('at+CGEQOSRDP', '.*CGEQOSRDP: 4.*OK'))


if "__main__" == __name__:
    unicorn.main()
