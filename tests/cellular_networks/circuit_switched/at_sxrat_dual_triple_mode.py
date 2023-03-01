#responsible: jingxin.shen@thalesgroup.com;shuang.liang@thalesgroup.com
#location: Beijing
#TC0102541.002

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import dstl_lock_sim,dstl_unlock_sim
'''
Case name:
'''


class at_sxrat_dual_triple_mode(BaseTest):
    def setup(test):
        #        test.dut.dstl_restart()
        #        test.sleep(5)
        pass

    def run(test):
        test.log.info('1.Check single mode: GSM network test <AcT>=0')
        test.log.info('1.1. Power on DUT without entering PIN code.')
        dstl_lock_sim(test.dut)
        test.expect(test.dut.dstl_restart())
        # global op_name
        # op_name = test.operator_name_numeric  # define in local.cfg,such as operator_name_numeric= '"45406"'
        test.dut.dstl_detect()

        global AcT, AcT1, AcT2, AcT3, dual_AcT1, dual_AcT2, dual_AcT3, triple_AcT
        AcT = 0
        if test.dut.product.upper() == "EXS82" or test.dut.product.upper() == "EXS62":
            AcT1 = 0
            AcT2 = 7
            AcT3 = 8
            dual_AcT1 = 9  # Cat.M/GSM
            dual_AcT2 = 10   # Cat.M/Cat.NB
            dual_AcT3 = 11   # Cat.NB/GSM
            triple_AcT = 12
        elif test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            AcT1 = 0
            AcT2 = 3
            AcT3 = 2
            dual_AcT3 = 1  # GSM/UMTS
            dual_AcT2 = 4  # UMTS/LTE
            dual_AcT1 = 5  # GSM/LTE
            triple_AcT = 6

        test.log.info('1.2. Set only <AcT> to GSM. Check if DUT returns OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? , expect DUT return ^SXRAT: 0,0 ')
        AcT = AcT1
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+str(AcT), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: '+ str(AcT) + ', ' + str(AcT)))

        test.log.info(
            '1.3. Set <AcT> to GSM,and <AcT_pref1> is not GSM,check if DUT returns +CME ERROR: invalid index.')
        AcT = AcT1
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+ str(AcT) + ',' + str(AcT2), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+ str(AcT) + ',' + str(AcT3), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+ str(AcT) + ',' + str(dual_AcT1), '+CME ERROR: invalid index'))

        test.log.info('1.4. Set <AcT> to GSM,and <AcT_pref1> is GSM,check if DUT returns OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? , expect DUT return ^SXRAT: 0,0 ')
        AcT = AcT1
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+ str(AcT) + ',' + str(AcT), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: '+ str(AcT) + ', ' + str(AcT)))

        test.log.info(
            '1.5.Set <AcT>and<AcT_pref1> to GSM, and <AcT_pref2> is GSM,check if DUT returns +CME ERROR: invalid index.')
        AcT = AcT1
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+ str(AcT) + ',' + str(AcT) + ',' + str(AcT), '+CME ERROR: invalid index'))

        test.log.info(
            '1.6.Set <AcT>and<AcT_pref1> to GSM, and <AcT_pref2> is not GSM,check if DUT returns +CME ERROR: invalid index. ')
        AcT = AcT1
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+ str(AcT) + ',' + str(AcT) + ',' + str(AcT2), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+ str(AcT) + ',' + str(AcT) + ',' + str(AcT3), '+CME ERROR: invalid index'))

        test.log.info(
            '1.7. Restart the DUT without entering PIN, check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 0,0')
        AcT = AcT1
        test.expect(test.dut.dstl_restart())
        time.sleep(15)
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: '+ str(AcT) + ', ' + str(AcT)))

        test.log.info(
            '1.8. Enable URC CGREG/CEREG mode 2. Enter PIN code and wait for register to the network. Check if DUT registers on GSM network. ')

        test.register_to_network_and_check(AcT)

        test.log.info(
            '1.9.After DUT is registered, check setting only <AcT>=0, 7 or 8 can be used to change the RAT instantly.')

        AcT = AcT2
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+str(AcT), 'OK'))
        time.sleep(15)
        if test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: [2,1,.*,.*,7| 2,4]'))
        else:
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,7'))

        AcT = AcT3
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+str(AcT), 'OK'))
        time.sleep(15)
        if test.dut.product.upper() == "EXS82" or test.dut.product.upper() == "EXS62":
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,9'))
        elif test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: 2,1,.*,.*,2'))

        test.log.info('2. Following step 1 to test <AcT>=7 ')
        test.expect(test.dut.dstl_restart())
        AcT = AcT2
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+str(AcT), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: '+ str(AcT) + ', ' + str(AcT)))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT1), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT3), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(dual_AcT1), '+CME ERROR: invalid index'))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: '+ str(AcT) + ', ' + str(AcT)))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT) + ',' + str(AcT), '+CME ERROR: invalid index'))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT) + ',' + str(AcT1), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT) + ',' + str(AcT3), '+CME ERROR: invalid index'))

        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: '+ str(AcT) + ', ' + str(AcT)))

        test.register_to_network_and_check(AcT)

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+str(AcT1), 'OK'))
        time.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: 2,1,.*,.*,0'))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+str(AcT3), 'OK'))
        time.sleep(10)
        if test.dut.product.upper() == "EXS82" or test.dut.product.upper() == "EXS62":
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,9'))
        elif test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: [2,1,.*,.*,2|2,4]'))


        test.log.info('3. Following step 1 to test <AcT>=8')
        test.expect(test.dut.dstl_restart())
        AcT = AcT3
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+str(AcT), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: '+ str(AcT) + ', ' + str(AcT)))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT1), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT2), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(dual_AcT1), '+CME ERROR: invalid index'))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(AcT) + ', ' + str(AcT)))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT) + ',' + str(AcT), '+CME ERROR: invalid index'))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT) + ',' + str(AcT1), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT) + ',' + str(AcT) + ',' + str(AcT2), '+CME ERROR: invalid index'))

        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: '+ str(AcT) + ', ' + str(AcT)))

        test.register_to_network_and_check(AcT)

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+str(AcT1), 'OK'))
        time.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: 2,1,.*,.*,0'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT='+str(AcT2), 'OK'))
        time.sleep(10)
        if test.dut.product.upper() == "EXS":
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,7'))
        elif test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: [2,1,.*,.*,7|2,4]'))

        test.log.info('4.Check dual mode: <AcT>=9,Cat.M1 / GSM dual mode test.')
        test.log.info('4.1. Power on DUT without entering PIN code.')
        test.expect(test.dut.dstl_restart())

        test.log.info(
            '4.2. Set <AcT> to Cat.M1 / GSM dual mode, and <AcT_pref1> is not Cat.M1 nor GSM, check if DUT returns +CME ERROR: invalid index.')

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ','+ str(AcT3), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ','+ str(dual_AcT1), '+CME ERROR: invalid index'))

        test.log.info(
            'Set <AcT> to Cat.M1 / GSM dual mode,<AcT_pref1> is Cat.M1 or GSM, and <AcT_pref2> is not Cat.M1 nor GSM,check if DUT return +CME ERROR: invalid index. ')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ','+ str(AcT2) + ','+ str(AcT3), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ','+ str(AcT1) + ','+ str(AcT3), '+CME ERROR: invalid index'))

        test.log.info(
            'Set <AcT> to Cat.M1 / GSM dual mode,<AcT_pref1> is GSM, and <AcT_pref2> is Cat.M1,check if DUT return +CME ERROR: invalid index. ')
        if test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ',' + str(AcT1) + ',' + str(AcT2),
                                                     'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ','+ str(AcT1) + ','+ str(AcT2), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ','+ str(AcT1) + ','+ str(AcT1), '+CME ERROR: invalid index'))

        test.log.info(
            'Set <AcT> to Cat.M1 / GSM dual mode,<AcT_pref1> is Cat.M1, and <AcT_pref2> is GSM,check if DUT return +CME ERROR: invalid index. ')
        if test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ','+ str(AcT2) + ','+ str(AcT1), 'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ','+ str(AcT2) + ','+ str(AcT2), '+CME ERROR: invalid index'))

        test.log.info('4.3. Set <AcT> to Cat.M1 / GSM dual mode, and <AcT_pref1> is Cat.M1, check if DUT returns OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 9,7,0  ')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ',' + str(AcT2), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT1) +', '+ str(AcT2) +', '+str(AcT1)))

        test.log.info(
            '4.4. Enable URC CGREG/CEREG mode 2. Enter PIN code and wait for register to the network. Check if DUT registers on Cat.M1 network.(it is possible that the ME registers to GSM if it is more suitable.)')

        test.register_to_network_and_check(dual_AcT1)

        test.log.info(
            '4.5. Restart the DUT without entering PIN, check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 9,7,0')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT1) +', '+ str(AcT2) +', '+str(AcT1)))

        test.log.info('4.6. Set <AcT> to Cat.M1 / GSM dual mode,and <AcT_pref1> is GSM,check if DUT returns OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 9,0,7   ')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ',' + str(AcT1), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT1) +', '+ str(AcT1) +', '+str(AcT2)))

        test.log.info(
            '4.7. Enable URC CGREG/CEREG mode 2. Enter PIN code and wait for register to the network. Check if DUT registers on GSM network.(it is possible that the ME registers to Cat.M1 if it is more suitable.)')
        test.register_to_network_and_check(dual_AcT1)
        test.log.info(
            '4.8. Restart the DUT without entering PIN, check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 9,0,7')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT1) +', '+ str(AcT1) +', '+str(AcT2)))

        test.log.info('4.9. Set only <AcT> to Cat.M1 / GSM dual mode, check if DUT returns OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 9,7,0')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT1) +', '+ str(AcT2) +', '+str(AcT1)))

        test.log.info(
            '4.10. Restart the DUT without entering PIN, check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 9,7,0')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT1) +', '+ str(AcT2) +', '+str(AcT1)))

        test.log.info('5.<AcT>=10:Following step 4 to test Cat.M1 / Cat.NB dual mode test.')
        test.log.info('In 5.9,expect DUT return ^SXRAT:10, 7, 8')

        test.expect(test.dut.dstl_restart())

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' +str(dual_AcT2) + ',' + str(AcT1), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' +str(dual_AcT2) + ',' + str(dual_AcT2), '+CME ERROR: invalid index'))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' +str(dual_AcT2) + ',' + str(AcT2) + ',' + str(AcT1), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' +str(dual_AcT2) + ',' + str(AcT3) + ',' + str(AcT1), '+CME ERROR: invalid index'))

        if test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT2) + ',' + str(AcT3) + ',' + str(AcT2),
                                                     'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' +str(dual_AcT2) + ',' + str(AcT3) + ',' + str(AcT2), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' +str(dual_AcT2) + ',' + str(AcT3) + ',' + str(AcT3), '+CME ERROR: invalid index'))

        if test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' +str(dual_AcT2) + ',' + str(AcT2) + ',' + str(AcT3), 'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT2) + ',' + str(AcT2) + ',' + str(AcT3),
                                                     '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' +str(dual_AcT2) + ',' + str(AcT2) + ',' + str(AcT2), '+CME ERROR: invalid index'))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' +str(dual_AcT2) + ',' + str(AcT2), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT2) +', '+ str(AcT2) +', '+str(AcT3)))

        test.register_to_network_and_check(dual_AcT2)

        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT2) +', '+ str(AcT2) +', '+str(AcT3)))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT2) + ',' + str(AcT3), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT2) +', '+ str(AcT3) +', '+str(AcT2)))

        test.register_to_network_and_check(dual_AcT2)

        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT2) +', '+ str(AcT3) +', '+str(AcT2)))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT2), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT2) +', '+ str(AcT2) +', '+str(AcT3)))

        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT2) +', '+ str(AcT2) +', '+str(AcT3)))

        test.log.info('6.<AcT>=11,Following step 4 to test Cat.NB / GSM dual mode test.')

        test.expect(test.dut.dstl_restart())

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT2), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(dual_AcT3), '+CME ERROR: invalid index'))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT1) + ',' + str(AcT2), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT3) + ',' + str(AcT2), '+CME ERROR: invalid index'))

        if test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT3) + ',' + str(AcT1), 'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT3) + ',' + str(AcT1),
                                                     '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT3) + ',' + str(AcT3), '+CME ERROR: invalid index'))

        if test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT1) + ',' + str(AcT3),
                                                     'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT1) + ',' + str(AcT3), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT1) + ',' + str(AcT1), '+CME ERROR: invalid index'))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT3) +', '+ str(AcT3) +', '+str(AcT1)))

        test.register_to_network_and_check(dual_AcT3)

        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT3) +', '+ str(AcT3) +', '+str(AcT1)))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT1), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT3) +', '+ str(AcT1) +', '+str(AcT3)))

        test.register_to_network_and_check(dual_AcT3)

        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT3) +', '+ str(AcT1) +', '+str(AcT3)))

        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT3) +', '+ str(AcT3) +', '+str(AcT1)))

        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(dual_AcT3) +', '+ str(AcT3) +', '+str(AcT1)))

        test.log.info('7. Check triple mode: <AcT>=12,Cat.M1 / Cat.NB/GSM triple mode test.')
        test.log.info('7.1. Power on DUT without entering PIN code.')
        test.expect(test.dut.dstl_restart())
        time.sleep(10)
        test.log.info(
            '7.2. Set <AcT> to Cat.M1 /Cat.NB1/ GSM triple mode,and <AcT_pref1> is not Cat.M1 /Cat.NB/ GSM ,check if DUT returns +CME ERROR: invalid index.')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(dual_AcT1), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(dual_AcT2), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(dual_AcT3), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(triple_AcT), '+CME ERROR: invalid index'))
        test.log.info(
            'Set <AcT> to Cat.M1 /Cat.NB1/ GSM triple mode,<AcT_pref1> is Cat.M1 /Cat.NB/ GSM ,and <AcT_pref2> is not Cat.M1 /Cat.NB1/ GSM ,check if DUT returns +CME ERROR: invalid index. ')
        #test.expect(test.dut.at1.send_and_verify('AT^SXRAT=12,0,2', '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT2) + ',' + str(dual_AcT1), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT3) + ',' + str(dual_AcT2), '+CME ERROR: invalid index'))

        test.log.info(
            'Set <AcT> to Cat.M1 /Cat.NB1/ GSM triple mode,<AcT_pref1> is Cat.M1 /Cat.NB/ GSM ,and <AcT_pref2> is same as <Act_pref1> ,check if DUT returns +CME ERROR: invalid index. ')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT1) + ',' + str(AcT1), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT2) + ',' +str( AcT2), '+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT3) + ',' + str(AcT3), '+CME ERROR: invalid index'))

        test.log.info('7.3. Set only <AcT> to Cat.M1 /Cat.NB1/ GSM triple mode,expect DUT return OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 12, 7, 8 ')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT2) +', '+str(AcT3)))
        test.log.info(
            'Set <AcT> to Cat.M1 /Cat.NB/ GSM triple mode,<AcT_pref1> is Cat.NB,<AcT_pref2> is not set, check if DUT return OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 12, 8, 7')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT3), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT3) +', '+str(AcT2)))
        test.log.info(
            'Set <AcT> to Cat.M1 /Cat.NB/ GSM triple mode,<AcT_pref1> is Cat.M1,<AcT_pref2> is not set, check if DUT return OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 12, 7, 8   ')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT2), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT2) +', '+str(AcT3)))

        test.log.info(
            'Set <AcT> to Cat.M1 /Cat.NB/ GSM triple mode,<AcT_pref1> is GSM,<AcT_pref2> is not set, check if DUT return OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 12, 0, 7   ')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT1), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT1) +', '+str(AcT2)))
        test.log.info(
            '7.4. Set <AcT> to Cat.M1 /Cat.NB/ GSM triple mode,<AcT_pref1> is Cat.M1,<AcT_pref2> is Cat.NB,check if DUT returns OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 12, 7, 8  ')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT2) + ',' + str(AcT3), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT2) +', '+str(AcT3)))

        test.log.info(
            '7.5. Enter PIN code and wait for register to the network. Check if DUT registers on Cat.M1 network.(it is possible that the ME registers to Cat.NB or GSM if it is more suitable.)')
        test.register_to_network_and_check(triple_AcT)
        test.log.info(
            '7.6. Restart the DUT without entering PIN, check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 12, 7, 8')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT2) +', '+str(AcT3)))

        test.log.info(
            '7.7. Set <AcT> to Cat.M1 /Cat.NB1/ GSM triple mode,and <AcT_pref1> is GSM, <AcT_pref2> is Cat.M1,check if DUT returns OK.')
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 12, 0, 7')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT1) + ',' + str(AcT2), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT1) +', '+str(AcT2)))
        test.log.info(
            '7.8. Enter PIN code and wait for register to the network. Check if DUT registers on GSM network.(it is possible that the ME registers to Cat.M1 or Cat.NB if it is more suitable.)')
        test.register_to_network_and_check(triple_AcT)
        test.log.info(
            '7.9. Restart the DUT without entering PIN, check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 12, 0, 7')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT1) +', '+str(AcT2)))
        test.log.info(
            '7.10.Set <AcT> to Cat.M1 /Cat.NB/ GSM triple mode,and <AcT_pref1> is Cat.NB,<AcT_pref2> is GSM, check if DUT returns OK.')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT3) + ',' + str(AcT1), 'OK'))
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 12, 8, 0   ')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT3) +', '+str(AcT1)))
        test.log.info(
            '7.11. Enter PIN code and wait for register to the network. Check if DUT registered on Cat.NB network.(it is possible that the ME registered to Cat.M1 or GSM if it is more suitable.)')
        test.register_to_network_and_check(triple_AcT)
        test.log.info(
            '7.12. Restart the DUT without entering PIN, check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 12, 8, 0')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT3) +', '+str(AcT1)))
        test.log.info(
            '7.13. Set <AcT> to Cat.M1 /Cat.NB1/ GSM triple mode,<AcT_pref1> is Cat.NB1,<AcT_pref2> is Cat.M1,check if DUT returns OK.')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT3) + ',' + str(AcT2), 'OK'))
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 12, 8, 7')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) + ', ' + str(AcT3) + ', ' + str(AcT2)))
        test.log.info(
            '7.14. Enter PIN code and wati for register to the network. Check if DUT registers on Cat.NB1 network.(it is possible that the ME registers to Cat.M or GSM if it is more suitable.)')
        test.register_to_network_and_check(triple_AcT)
        test.log.info(
            '7.15. Restart the DUT without entering PIN, check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 12, 8, 7')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', '+ str(AcT3) +', '+str(AcT2)))
        test.log.info(
            '7.16. Set <AcT> to Cat.M1 /Cat.NB1/ GSM triple mode,and <AcT_pref1> is Cat.M1, <AcT_pref2> is GSM,check if DUT returns OK.')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT2) + ',' + str(AcT1), 'OK'))
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 12, 7, 0')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) + ', ' + str(AcT2) + ', ' + str(AcT1)))
        test.log.info(
            '7.17. Enter PIN code and wait for register to the network. Check if DUT registers on Cat.M1 network.(it is possible that the ME registers to GSM or Cat.NB if it is more suitable.)')
        test.register_to_network_and_check(triple_AcT)
        test.log.info(
            '7.18. Restart the DUT without entering PIN, check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 12, 7, 0')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) + ', ' + str(AcT2) + ', ' + str(AcT1)))
        test.log.info(
            '7.19.Set <AcT> to Cat.M1 /Cat.NB1/ GSM triple mode,and <AcT_pref1> is GSM,<AcT_pref2> is Cat.NB1, check if DUT returns OK.')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT1) + ',' + str(AcT3), 'OK'))
        test.log.info('Check the current parameter value using AT^SXRAT? ,expect DUT returns ^SXRAT: 12, 0, 8   ')
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', ' + str(AcT1) + ', ' + str(AcT3)))
        test.log.info(
            '7.20. Enter PIN code and wait for register to the network. Check if DUT registered on GSM network.(it is possible that the ME registered to Cat.M1 or Cat.NB if it is more suitable.)')

        test.register_to_network_and_check(triple_AcT)
        test.log.info(
            '7.21. Restart the DUT without entering PIN, check the current parameter value using AT^SXRAT? ,expect DUT return ^SXRAT: 12, 0, 8')
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) +', ' + str(AcT1) + ', ' + str(AcT3)))
        time.sleep(5)
        test.log.info(
            '8. Check AT^SXRAT command in airplane mode. read and test command can be used, but not the write command.')
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', '^SYSSTART AIRPLANE MODE'))

        if test.dut.product.upper() == "EXS":
            test.expect(test.dut.at1.send_and_verify('at^sxrat=?', '^SXRAT: (0,7-12), (0,7,8), (0,7,8)'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat?', '^SXRAT: 12, 0, 8'))
        elif test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('at^sxrat=?', '^SXRAT: (0-6), (0,2,3), (0,2,3)'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat?', '^SXRAT: 6, 0, 2'))
        if test.dut.product.upper() == "EXS":
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(AcT1), '+CME ERROR: operation not allowed'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(AcT2), '+CME ERROR: operation not allowed'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(AcT3), '+CME ERROR: operation not allowed'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(dual_AcT1) + ',' + str(AcT1), '+CME ERROR: operation not allowed'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(dual_AcT2) + ',' + str(AcT3), '+CME ERROR: operation not allowed'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(dual_AcT3) + ',' + str(AcT3), '+CME ERROR: operation not allowed'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(triple_AcT) + ',' + str(AcT2) + ',' + str(AcT3), '+CME ERROR: operation not allowed'))
        elif test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(AcT1), 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(AcT2), 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(AcT3), 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(dual_AcT1) + ',' + str(AcT1), 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(dual_AcT2) + ',' + str(AcT3), 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(dual_AcT3) + ',' + str(AcT3), 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(triple_AcT) + ',' + str(AcT2) + ',' + str(AcT3), 'OK'))
        if test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', '.*OK'))
        test.log.info('9. Check RAT change by cops command')
        test.check_cops_change_rat()
        test.log.info('Test end!')

    def check_cops_change_rat(test):

        test.dut.dstl_restart()
        time.sleep(3)
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('at+creg=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cereg=2', 'OK'))
        i=1
        while(i<4):
            if test.dut.product.upper() == "EXS82" or test.dut.product.upper() == "EXS62":
                if i == 1:
                    act = "GSM"
                elif i == 2:
                    act = "CATM"
                else:
                    act = "CATNB"
            elif test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
                if i == 1:
                    act = "GSM"
                elif i == 2:
                    act = "LTE"
                else:
                    act = "UMTS"

            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT2), 'OK'))
            test.register_manually_and_check(act)
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT3), 'OK'))
            test.register_manually_and_check(act)
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT1), 'OK'))
            test.register_manually_and_check(act)
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ',' + str(AcT2), 'OK'))
            test.register_manually_and_check(act)
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT2) + ',' + str(AcT2), 'OK'))
            test.register_manually_and_check(act)
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT3) + ',' + str(AcT3), 'OK'))
            test.register_manually_and_check(act)
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(triple_AcT) + ',' + str(AcT2) + ',' + str(AcT3), 'OK'))
            test.register_manually_and_check(act)
            i=i+1
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(AcT3), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK'))
        if test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT?',
                                                     '^SXRAT: ' + str(AcT3) + ', ' + str(AcT3)))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) + ', ' + str(AcT3) + ', ' + str(AcT2)))
        test.expect(test.dut.at1.send_and_verify('AT^SXRAT=' + str(dual_AcT1) + ',' + str(AcT1), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK'))
        if test.dut.product.upper() == "PLS83" or test.dut.product.upper() == "PLS63":
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT?',
                                                     '^SXRAT: ' + str(dual_AcT1) + ', ' + str(AcT1) + ', ' + str(
                                                         AcT2)))
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', '^SXRAT: ' + str(triple_AcT) + ', ' + str(AcT1) + ', ' + str(AcT2)))
        return

    def register_manually_and_check(test,act):
#        op_name = test.operator_name_numeric #define in local.cfg,such as operator_name_numeric= '"45406"'
        if act is 'GSM':
            test.expect(test.dut.at1.send_and_verify('at+cops=,,,0', 'OK'))
            time.sleep(10)
            test.expect(test.dut.at1.send_and_verify('AT+CREG?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat?', '^SXRAT: 0, 0'))
        elif act is 'CATM':
            test.expect(test.dut.at1.send_and_verify('at+cops=,,,7', 'OK'))
            time.sleep(10)
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat?', '^SXRAT: 7, 7'))
        elif act is 'CATNB':
            test.expect(test.dut.at1.send_and_verify('at+cops=,,,9', 'OK'))
            time.sleep(10)
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat?', '^SXRAT: 8, 8'))
        elif act is 'LTE':
            test.expect(test.dut.at1.send_and_verify('at+cops=,,,7', 'OK'))
            time.sleep(10)
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat?', '^SXRAT: 3, 3'))
        elif act is 'UMTS':
            test.expect(test.dut.at1.send_and_verify('at+cops=,,,2', 'OK'))
            time.sleep(10)
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^sxrat?', '^SXRAT: 2, 2'))

        return

    def register_to_network_and_check(test, rat):
        time.sleep(3)
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CEREG=2', 'OK'))
        time.sleep(20)

        if rat == 12:
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,' + str(9)) or test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,' + str(7))or test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: 2,1,.*,.*,' + str(0)))

        elif rat == 11:
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,' + str(9))or test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: 2,1,.*,.*,' + str(0)))

        elif rat == 10:
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,' + str(9)) or test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,' + str(7)))

        elif rat == 9:
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,' + str(7)) or test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: 2,1,.*,.*,' + str(0)))

        elif rat == 8:
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,' + str(9)))

        elif rat == 1:
            test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: 2,1,.*,.*,[2|0]'))

        elif rat == 4:
            test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: 2,1,.*,.*,[2|7]'))

        elif rat == 5:
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?','.*CEREG: (2,1,.*,.*,[0|7])|(2,4)'))

        elif rat == 6:
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: (2,1,.*,.*,[0|7|2])|(2,4)'))

        elif rat == 2:
            test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: 2,1,.*,.*,2'))

        elif rat == 3:
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: [2,1,.*,.*,7|2,4]'))
        else:
            if rat==0:
                test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*CREG: 2,1,.*,.*,0'))

            else:#rat==7
                test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '.*CEREG: 2,1,.*,.*,'+str(7)))

    def cleanup(test):
        dstl_unlock_sim(test.dut)


if (__name__ == "__main__"):
    unicorn.main()
