# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0084469.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service.register_to_network import dstl_register_to_umts
from dstl.auxiliary import init
import re


class Test(BaseTest):
    """
    TC0084469.001 -  QoSRel99
    Ensure, that the SUT is able to establish GPRS dial-up connections by the negotiation of different quality of
    service profiles for 3rd generation networks.
    """

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        test.dut.dstl_register_to_network()
        test.apn = test.dut.sim.gprs_apn
        test.apn2 = test.dut.sim.gprs_apn_2
        test.log.info('*** TestCase: TC0084469.001 -  QoSRel99 Start ***')
        pass

    def run(test):
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        # UMTS is switch off in germany
        #test.expect(dstl_register_to_umts(test.dut))
        test.expect(test.dut.dstl_register_to_network())
        test.log.step('delete qos profiles')
        for cid in range(1, 17):
            test.delete_cgqreq_cgqmin_profile(cid)
        test.log.step('1.define all possible PDP contexts')
        for cid in range(1, 17):
            test.set_pdp_context(cid, test.apn)

        test.log.step('2.set all QoS parameters to minimum values')
        min_cgqreq_precedence_value, min_cgqreq_delay_value, min_cgqreq_reliability_value, min_cgqreq_peak_value, \
        min_cgqreq_mean_value = test.get_min_cgqreq_parameter()
        min_cgqmin_precedence_value, min_cgqmin_delay_value, min_cgqmin_reliability_value, min_cgqmin_peak_value, \
        min_cgqreq_mean_value = test.get_min_cgqmin_parameter()

        for cid in range(1, 17):
            test.set_cgqreq_param(cid, min_cgqreq_precedence_value, min_cgqreq_delay_value,
                                  min_cgqreq_reliability_value, min_cgqreq_peak_value, min_cgqreq_mean_value)
            test.set_cgqmin_param(cid, min_cgqmin_precedence_value, min_cgqmin_delay_value,
                                  min_cgqmin_reliability_value, min_cgqmin_peak_value, min_cgqreq_mean_value)
        test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '.*OK.*'))

        test.log.step('3.try to set several illegal QoS profiles (shall be rejected)')
        max_cgqreq_precedence_value, max_cgqreq_delay_value, max_cgqreq_reliability_value, max_cgqreq_peak_value, \
        max_cgqreq_mean_value = test.get_max_cgqreq_parameter()
        max_cgqmin_precedence_value, max_cgqmin_delay_value, max_cgqmin_reliability_value, max_cgqmin_peak_value, \
        max_cgqreq_mean_value = test.get_max_cgqmin_parameter()

        test.invalid_param_cgqreq_test('17')
        test.invalid_param_cgqmin_test('17')
        test.invalid_param_cgqreq_test('0')
        test.invalid_param_cgqmin_test('0')
        test.invalid_param_cgqreq_test('1,' + str(int(max_cgqreq_precedence_value) + 1))
        test.invalid_param_cgqmin_test('1,' + str(int(max_cgqmin_precedence_value) + 1))
        test.invalid_param_cgqreq_test('1,' + str(int(min_cgqreq_precedence_value) - 1))
        test.invalid_param_cgqmin_test('1,' + str(int(min_cgqmin_precedence_value) - 1))
        test.invalid_param_cgqreq_test('2,1,' + str(int(max_cgqreq_delay_value) + 1))
        test.invalid_param_cgqmin_test('2,1,' + str(int(max_cgqmin_delay_value) + 1))
        test.invalid_param_cgqreq_test('2,1,' + str(int(min_cgqreq_delay_value) - 1))
        test.invalid_param_cgqmin_test('2,1,' + str(int(min_cgqmin_delay_value) - 1))
        test.invalid_param_cgqreq_test('2,1,3,' + str(int(max_cgqmin_reliability_value) + 1))
        test.invalid_param_cgqmin_test('2,1,3,' + str(int(max_cgqmin_reliability_value) + 1))
        test.invalid_param_cgqreq_test('2,1,3,' + str(int(min_cgqmin_reliability_value) - 1))
        test.invalid_param_cgqmin_test('2,1,3,' + str(int(min_cgqmin_reliability_value) - 1))
        test.invalid_param_cgqreq_test('2,1,3,5,' + str(int(max_cgqreq_peak_value) + 1))
        test.invalid_param_cgqmin_test('2,1,3,5,' + str(int(max_cgqreq_peak_value) + 1))
        test.invalid_param_cgqreq_test('2,1,3,5,' + str(int(min_cgqreq_peak_value) - 1))
        test.invalid_param_cgqmin_test('2,1,3,5,' + str(int(min_cgqreq_peak_value) - 1))
        test.invalid_param_cgqreq_test('2,1,3,5,7,' + str(int(max_cgqreq_mean_value) + 1))
        test.invalid_param_cgqmin_test('2,1,3,5,7,' + str(int(max_cgqreq_mean_value) + 1))
        test.invalid_param_cgqreq_test('2,1,3,5,7,' + str(int(min_cgqreq_mean_value) - 1))
        test.invalid_param_cgqmin_test('2,1,3,5,7,' + str(int(min_cgqreq_mean_value) - 1))

        test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqmin?', '.*OK.*'))

        test.log.info('4.test several legal QoS profiles as follows:'
                      'set the minimum acceptable QoS profile to network subscribed'
                      'activate the related PDP context'
                      'deactivate the active PDP context'
                      'set the minimum acceptable QoS profile to maximum values'
                      'try to activate the related PDP context (shall be rejected)'
                      'continue with the next QoS profile')

        for cid in range(1, 17):

            test.log.info('4.1.' + str(cid) + ' set the minimum acceptable QoS profile to network subscribed')
            test.set_cgqreq_param(cid, min_cgqreq_precedence_value, min_cgqreq_delay_value,
                                  min_cgqreq_reliability_value, min_cgqreq_peak_value, min_cgqreq_mean_value)
            test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '.*OK.*'))
            test.set_cgqmin_param(cid, min_cgqmin_precedence_value, min_cgqmin_delay_value,
                                  min_cgqmin_reliability_value, min_cgqmin_peak_value, min_cgqreq_mean_value)
            test.expect(test.dut.at1.send_and_verify('at+cgqmin?', '.*OK.*'))

            if test.dut.project == 'VIPER':
                test.log.info('4.2.' + str(cid) + ' activate the related PDP context')
                test.expect(test.dut.at1.send_and_verify(f'at+cgact=1,{cid}', 'OK'))
                test.sleep(2)
                test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},1'))
                test.log.info('4.3.' + str(cid) + ' deactivate the active PDP context')
                test.expect(test.dut.at1.send_and_verify(f'at+cgact=0,{cid}', 'OK'))
                test.sleep(2)
                test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},0'))
            else:
                test.log.info('4.2.' + str(cid) + ' activate the related PDP context')
                test.expect(test.dut.at1.send_and_verify(f'at+cgact=1,{cid}', 'OK'))
                test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},1'))
                test.log.info('4.3.' + str(cid) + ' deactivate the active PDP context')
                test.expect(test.dut.at1.send_and_verify(f'at+cgact=0,{cid}', 'OK'))
                test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},0'))

            test.log.info('4.4.' + str(cid) + ' set the minimum acceptable LTE QoS profile to maximum values')
            test.set_cgqreq_param(cid, max_cgqreq_precedence_value, max_cgqreq_delay_value,
                                  max_cgqreq_reliability_value, max_cgqreq_peak_value, max_cgqreq_mean_value)
            test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '.*OK.*'))
            test.set_cgqmin_param(cid, max_cgqmin_precedence_value, max_cgqmin_delay_value,
                                  max_cgqmin_reliability_value, max_cgqmin_peak_value, max_cgqreq_mean_value)
            test.expect(test.dut.at1.send_and_verify('at+cgqmin?', '.*OK.*'))

            if test.dut.project == 'VIPER':
                test.log.info('4.2a.' + str(cid) + ' activate the related PDP context.')
                test.expect(test.dut.at1.send_and_verify(f'at+cgact=1,{cid}', 'ERROR'))
                test.sleep(2)
                test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},0'))
                test.log.info('4.3a.' + str(cid) + ' deactivate the active PDP context.')
                test.expect(test.dut.at1.send_and_verify(f'at+cgact=0,{cid}', 'OK'))
                test.sleep(2)
                test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},0'))

            else:
                test.log.info('4.2a.' + str(cid) + ' activate the related PDP context.')
                test.expect(test.dut.at1.send_and_verify(f'at+cgact=1,{cid}', 'ERROR'))
                test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},1'))

                test.log.info('4.3a.' + str(cid) + ' deactivate the active PDP context.')
                test.expect(test.dut.at1.send_and_verify(f'at+cgact=0,{cid}', 'OK'))
                test.expect(test.dut.at1.send_and_verify('at+cgact?', f'CGACT: {cid},0'))
        pass

    def cleanup(test):
        test.log.info('*** TestCase: TC0084469.001 -  QoSRel99 End***')
        pass

    def set_pdp_context(test, cid, apn):
        test.expect(test.dut.at1.send_and_verify(f'at+cgdcont={cid},"IP","{apn}"', 'OK'))
        return

    def delete_cgqreq_cgqmin_profile(test, cid):
        test.expect(test.dut.at1.send_and_verify(f'at+cgqreq={cid}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'at+cgqmin={cid}', 'OK'))
        return

    def get_max_cgqreq_parameter(test):
        test.dut.at1.send_and_verify('at+cgqreq=?', 'OK')
        res = test.dut.at1.last_response
        pattern = '.*CGQREQ: .*,\\(0-(\d+)\\),\\(0-(\d+)\\),\\(0-(\d+)\\),\\(0-(\d+)\\),\\(0-\d+\,(\d+)\\).*'

        max_ceqreq_precedence = re.search(pattern, res).group(1)
        max_ceqreq_delay = re.search(pattern, res).group(2)
        max_ceqreq_reliability = re.search(pattern, res).group(3)
        max_ceqreq_peak = re.search(pattern, res).group(4)
        max_ceqreq_mean = re.search(pattern, res).group(5)

        test.log.info('Max CEQREQ PRECEDENCE: {}\n Max CEQREQ DELAY: {}\n Max CEQREQ RELIABILITY: {}\n '
                      'Max CEQREQ PEAK: {}\n Max CEQREQ MEAN: {}'.format(max_ceqreq_precedence, max_ceqreq_delay,
                                                                         max_ceqreq_reliability, max_ceqreq_peak,
                                                                         max_ceqreq_mean))
        return max_ceqreq_precedence, max_ceqreq_delay, max_ceqreq_reliability, max_ceqreq_peak, max_ceqreq_mean

    def get_max_cgqmin_parameter(test):
        test.dut.at1.send_and_verify('at+cgqmin=?', 'OK')
        res = test.dut.at1.last_response
        pattern = '.*CGQMIN: .*,\\(0-(\d+)\\),\\(0-(\d+)\\),\\(0-(\d+)\\),\\(0-(\d+)\\),\\(0-\d+\,(\d+)\\).*'

        max_cgqmin_precedence = re.search(pattern, res).group(1)
        max_cgqmin_delay = re.search(pattern, res).group(2)
        max_cgqmin_reliability = re.search(pattern, res).group(3)
        max_cgqmin_peak = re.search(pattern, res).group(4)
        max_cgqmin_mean = re.search(pattern, res).group(5)

        test.log.info('Max CEQMIN PRECEDENCE: {}\n Max CEQREQ DELAY: {}\n Max CEQREQ RELIABILITY: {}\n '
                      'Max CEQREQ PEAK: {}\n Max CEQREQ MEAN: {}'.format(max_cgqmin_precedence, max_cgqmin_delay,
                                                                         max_cgqmin_reliability, max_cgqmin_peak,
                                                                         max_cgqmin_mean))

        return max_cgqmin_precedence, max_cgqmin_delay, max_cgqmin_reliability, max_cgqmin_peak, max_cgqmin_mean

    def get_min_cgqreq_parameter(test):
        test.dut.at1.send_and_verify('at+cgqreq=?', 'OK')
        res = test.dut.at1.last_response
        pattern = '.*CGQREQ: .*,\\((\d+)-\d+\\),\\((\d+)-\d+\\),\\((\d+)-\d+\\),\\((\d+)-\d+\\),\\((\d+)-\d+\,\d+\\).*'

        min_cgqreq_precedence = re.search(pattern, res).group(1)
        min_cgqreq_delay = re.search(pattern, res).group(2)
        min_cgqreq_reliability = re.search(pattern, res).group(3)
        min_cgqreq_peak = re.search(pattern, res).group(4)
        min_cgqreq_mean = re.search(pattern, res).group(5)

        test.log.info(
            'Min CEQREQ PRECEDENCE: {}\n Min CEQREQ DELAY: {}\n Min CEQREQ RELIABILITY: {}\n Min CEQREQ PEAK: {}\n '
            'Min CEQREQ MEAN: {}'.format(min_cgqreq_precedence, min_cgqreq_delay,
                                         min_cgqreq_reliability, min_cgqreq_peak, min_cgqreq_mean))
        return min_cgqreq_precedence, min_cgqreq_delay, min_cgqreq_reliability, min_cgqreq_peak, min_cgqreq_mean

    def get_min_cgqmin_parameter(test):
        test.dut.at1.send_and_verify('at+cgqmin=?', 'OK')
        res = test.dut.at1.last_response
        pattern = '.*CGQMIN: .*,\\((\d+)-\d+\\),\\((\d+)-\d+\\),\\((\d+)-\d+\\),\\((\d+)-\d+\\),\\((\d+)-\d+\,\d+\\).*'

        min_cgqmin_precedence = re.search(pattern, res).group(1)
        min_cgqmin_delay = re.search(pattern, res).group(2)
        min_cgqmin_reliability = re.search(pattern, res).group(3)
        min_cgqmin_peak = re.search(pattern, res).group(4)
        min_cgqmin_mean = re.search(pattern, res).group(5)

        test.log.info(
            'Min CEQMIN PRECEDENCE: {}\n Min CEQREQ DELAY: {}\n Min CEQREQ RELIABILITY: {}\n Min CEQREQ PEAK: {}\n '
            'Min CEQREQ MEAN: {}'.format(min_cgqmin_precedence, min_cgqmin_delay, min_cgqmin_reliability,
                                         min_cgqmin_peak, min_cgqmin_mean))

        return min_cgqmin_precedence, min_cgqmin_delay, min_cgqmin_reliability, min_cgqmin_peak, min_cgqmin_mean

    def invalid_param_cgqreq_test(test, params):
        test.expect(test.dut.at1.send_and_verify(f'at+cgqreq={params}', 'ERROR'))

    def invalid_param_cgqmin_test(test, params):
        test.expect(test.dut.at1.send_and_verify(f'at+cgqmin={params}', 'ERROR'))

    def set_cgqreq_param(test, cid, min_cgqreq_precedence_value, min_cgqreq_delay_value,
                         min_cgqreq_reliability_value, min_cgqreq_peak_value, min_cgqreq_mean_value):
        test.expect(test.dut.at1.send_and_verify(f'at+cgqreq={cid},{min_cgqreq_precedence_value},'
                                                 f'{min_cgqreq_delay_value},{min_cgqreq_reliability_value},'
                                                 f'{min_cgqreq_peak_value},{min_cgqreq_mean_value}', 'OK'))

    def set_cgqmin_param(test, cid, min_cgqmin_precedence_value, min_cgqmin_delay_value,
                         min_cgqmin_reliability_value, min_cgqmin_peak_value, min_cgqmin_mean_value):
        test.expect(test.dut.at1.send_and_verify(f'at+cgqmin={cid},{min_cgqmin_precedence_value},'
                                                 f'{min_cgqmin_delay_value},{min_cgqmin_reliability_value},'
                                                 f'{min_cgqmin_peak_value},{min_cgqmin_mean_value}', 'OK'))


if "__main__" == __name__:
    unicorn.main()
