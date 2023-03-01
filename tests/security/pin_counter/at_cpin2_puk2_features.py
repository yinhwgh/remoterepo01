# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091840.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import unlock_sim_pin2
from dstl.phonebook import phonebook_handle


class Test(BaseTest):
    """
    TC0091840.001 - TpAtCPin2Puk2Features
    Intention:
    Tests for CPIN2-Features with CPIN2 and CPUK2 entering.
    Subscriber: 1
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.simpin2 = test.dut.sim.pin2
        test.simpuk2 = test.dut.sim.puk2
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.dut.dstl_enter_pin()
        test.sleep(3)
        if test.dut.project is 'VIPER':
            test.errorcode = '.*\+CME ERROR: (incorrect password|unknown).*'
            test.cacm_write_resp = ".*CME ERROR: unknown.*"
            test.camm_write_resp = ".*CME ERROR: unknown.*"
            test.log.warning(" defect is accepted, see: VPR02-720: would not fix")
        else:
            test.cacm_write_resp = ".*OK.*"
            test.camm_write_resp = "OK"
            test.errorcode = '.*\+CME ERROR: incorrect password.*'
        pass

    def run(test):
        if test.simpin2 != 'None' and test.simpuk2 != 'None':
            test.log.info(f'Sim card PIN2:{test.simpin2}, PUK2:{test.simpuk2}')
        else:
            test.expect(False, critical=True, msg='Sim card info missing, please check!')

        test.log.step('1. Start Test CACM')
        if test.dut.project is 'VIPER':
            test.log.warning(" do not run this section, defect was accepted, see VPR02-720")
        else:
            test.check_cacm()

        test.log.step('2. Start Test CAMM')
        if test.dut.project is 'VIPER':
            test.log.warning(" do not run this section, defect was accepted, see: IPIS100358100")
        else:
            test.check_camm()

        test.log.step('3. Start Test CLCK-FD')
        test.check_clck_fd()

        test.log.step('4. Start Test CPUC')

        result = test.check_cpuc_read_resp(".*OK.*")
        if result:
            test.check_cpuc()
        else:
            test.log.info('Not support, skip.')

    def cleanup(test):
        test.dut.at1.send_and_verify('at^spic')
        test.dut.at1.send_and_verify('at^spic?')
        if 'SIM PIN' in test.dut.at1.last_response or 'SIM PUK' in test.dut.at1.last_response:
            test.dut.dstl_enter_pin()

        test.dut.at1.send_and_verify('at^spic')
        test.dut.at1.send_and_verify('at^spic?')
        if 'SIM PIN2' in test.dut.at1.last_response or 'SIM PUK2' in test.dut.at1.last_response:
            test.dut.dstl_enter_pin2()
        pass

    def check_cacm(test):
        test.log.step('1.1 CACM -activate feature without PIN2')
        test.expect(test.dut.at1.send_and_verify("AT+CACM?", ".*\+CACM: .*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CACM=", ".*\+CME ERROR: SIM PIN2 required.*"))

        test.log.step('1.2 CACM -enter wrong PIN2')
        test.expect(test.dut.at1.send_and_verify("AT+CACM=\"0454\"", test.errorcode))

        test.log.step('1.3 CACM -ENTERING CPIN2 WITHIN FEATURE-COMMAND')
        if test.dut.project is 'VIPER':
            test.expect(test.dut.at1.send_and_verify(f"AT+CACM=\"{test.simpin2}\"", ".*O.*"))
            test.expect(test.dut.at1.send_and_verify('at^spic?'))
        else:
            test.expect(test.dut.at1.send_and_verify(f"AT+CACM=\"{test.simpin2}\"", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CACM?", ".*\+CACM: \"000000\".*OK.*"))

        test.log.step('1.4 CACM -ENTERING CPIN2 OVER CPIN-COMMAND')
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.dut.dstl_enter_pin2()
        test.attempt(test.dut.at1.send_and_verify, "AT+CACM=", test.cacm_write_resp, retry=5, sleep=1)

        test.log.step('1.5 CACM -ENTERING PUK2 FOR CPIN2-FEATURE')
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.sleep(7)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CACM=\"0454\"", test.errorcode))
        test.expect(test.dut.at1.send_and_verify("AT+CACM=\"0454\"", test.errorcode))
        test.expect(test.dut.at1.send_and_verify("AT+CACM=\"0454\"", test.errorcode))
        if test.dut.dstl_support_at_cpin2():
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN2=\"{test.simpuk2}\",\"{test.simpin2}\"", "OK"))
        else:
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN=\"{test.simpuk2}\",\"{test.simpin2}\"", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CACM=", test.cacm_write_resp))
        pass

    def check_camm(test):
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.log.step('2.1 CAMM -activate feature without PIN2')
        test.attempt(test.dut.at1.send_and_verify, "AT+CAMM?", ".*\+CAMM: .*OK.*", retry=5, sleep=1)
        test.expect(test.dut.at1.send_and_verify("AT+CAMM=\"111111\"", ".*\+CME ERROR: SIM PIN2 required.*"))

        test.log.step('2.2 CAMM -enter wrong PIN2')
        test.expect(test.dut.at1.send_and_verify("AT+CAMM=\"111111\",\"0454\"", test.errorcode))

        test.log.step('2.3 CAMM -ENTERING CPIN2 WITHIN FEATURE-COMMAND')
        test.expect(test.dut.at1.send_and_verify(f"AT+CAMM=\"777777\",\"{test.simpin2}\"", test.camm_write_resp))
        ret = test.expect(test.dut.at1.send_and_verify("AT+CAMM?", ".*\+CAMM: \"777777\".*OK.*"))
        if not ret:
            test.expect(test.dut.at1.send_and_verify('at^spic'))
            test.expect(test.dut.at1.send_and_verify('at^spic?'))

        test.log.step('2.4 CAMM -ENTERING CPIN2 OVER CPIN-COMMAND')
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.dut.dstl_enter_pin2()
        if test.dut.project is 'VIPER':
            test.sleep(11)
        test.expect(test.dut.at1.send_and_verify(f"AT+CAMM=\"111111\"", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CAMM?", ".*\+CAMM: \"111111\".*OK.*"))

        test.log.step('2.5 CAMM -ENTERING PUK2 FOR CPIN2-FEATURE')
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.attempt(test.dut.at1.send_and_verify, "AT+CAMM=\"111111\",\"0454\"", test.errorcode, retry=5, sleep=1)
        test.expect(test.dut.at1.send_and_verify("AT+CAMM=\"111111\",\"0454\"", test.errorcode))
        test.expect(test.dut.at1.send_and_verify("AT+CAMM=\"111111\",\"0454\"", test.errorcode))
        if test.dut.dstl_support_at_cpin2():
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN2=\"{test.simpuk2}\",\"{test.simpin2}\"", "OK"))
        else:
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN=\"{test.simpuk2}\",\"{test.simpin2}\"", "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CAMM=\"666666\"", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CAMM?", ".*\+CAMM: \"666666\".*OK.*"))
        pass

    def check_clck_fd(test):
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.log.step('3.1 CLCK-FD -activate feature without PIN2')
        test.expect(test.dut.at1.send_and_verify("AT+CLCK=\"FD\",2", ".*\+CLCK: .*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"FD\"", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=1,\"12345\"", ".*\+CME ERROR: SIM PIN2 required.*"))

        test.log.step('3.2 CLCK-FD -enter wrong PIN2')
        test.expect(test.dut.at1.send_and_verify("AT+CLCK=\"FD\",1,\"0454\"", test.errorcode))

        test.log.step('3.3 CLCK-FD -ENTERING CPIN2 WITHIN FEATURE-COMMAND')
        test.expect(test.dut.at1.send_and_verify(f"AT+CLCK=\"FD\",1,\"{test.simpin2}\"", "OK"))
        test.fd_pb_check()
        test.expect(test.dut.at1.send_and_verify(f"AT+CLCK=\"FD\",0,\"{test.simpin2}\"", "OK"))

        test.log.step('3.4 CLCK-FD -ENTERING CPIN2 OVER CPIN-COMMAND')
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.dut.dstl_enter_pin2()
        test.sleep(5)
        test.fd_pb_check()

        test.log.step('3.5 CLCK-FD -ENTERING PUK2 FOR CPIN2-FEATURE')
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CLCK=\"FD\",1,\"0454\"", test.errorcode))
        test.expect(test.dut.at1.send_and_verify("AT+CLCK=\"FD\",1,\"0454\"", test.errorcode))
        test.expect(test.dut.at1.send_and_verify("AT+CLCK=\"FD\",1,\"0454\"", 'CME ERROR: SIM PUK2 required'))
        if test.dut.dstl_support_at_cpin2():
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN2=\"{test.simpuk2}\",\"{test.simpin2}\"", "OK"))
        else:
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN=\"{test.simpuk2}\",\"{test.simpin2}\"", "OK"))
        test.fd_pb_check()
        pass

    def check_cpuc(test):
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.log.step('4.1 CPUC -activate feature without PIN2')
        test.sleep(9)
        # test.expect(test.dut.at1.send_and_verify("AT+CPUC?", ".*OK.*"))
        test.check_cpuc_read_resp(".*OK.*")
        test.expect(test.dut.at1.send_and_verify("AT+CPUC=\"bcd\",\"1.23\"", ".*\+CME ERROR: SIM PIN2 required.*"))

        test.log.step('4.2 CPUC -enter wrong PIN2')
        test.expect(test.dut.at1.send_and_verify("AT+CPUC=\"bcd\",\"1.23\",\"0454\"", test.errorcode))

        test.log.step('4.3 CPUC -ENTERING CPIN2 WITHIN FEATURE-COMMAND')
        test.expect(test.dut.at1.send_and_verify(f"AT+CPUC=\"bcd\",\"1.23\",\"{test.simpin2}\"", "OK"))
        # test.expect(test.dut.at1.send_and_verify("AT+CPUC?", ".*\+CPUC: \"bcd\",\"1.23\".*OK.*"))
        test.check_cpuc_read_resp(".*\+CPUC: \"bcd\",\"1.23\".*OK.*")

        test.log.step('4.4 CPUC -ENTERING CPIN2 OVER CPIN-COMMAND')
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.dut.dstl_enter_pin2()
        if test.dut.project is 'VIPER':
            test.sleep(9)
        test.expect(test.dut.at1.send_and_verify("AT+CPUC=\"EUR\",\"2.23\"", "OK"))
        # test.expect(test.dut.at1.send_and_verify("AT+CPUC?", ".*\+CPUC: \"EUR\",\"2.23\".*OK.*"))
        test.check_cpuc_read_resp(".*\+CPUC: \"EUR\",\"2.23\".*OK.*")

        test.log.step('4.5 CPUC -ENTERING PUK2 FOR CPIN2-FEATURE')
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        if test.dut.project is 'VIPER':
            test.sleep(9)

        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPUC=\"EUR\",\"1.23\",\"0454\"", test.errorcode))
        test.expect(test.dut.at1.send_and_verify("AT+CPUC=\"EUR\",\"1.23\",\"0454\"", test.errorcode))
        test.expect(test.dut.at1.send_and_verify("AT+CPUC=\"EUR\",\"1.23\",\"0454\"", test.errorcode))
        if test.dut.dstl_support_at_cpin2():
            ret = test.expect(test.dut.at1.send_and_verify(f"AT+CPIN2=\"{test.simpuk2}\",\"{test.simpin2}\"", "OK"))
        else:
            ret = test.expect(test.dut.at1.send_and_verify(f"AT+CPIN=\"{test.simpuk2}\",\"{test.simpin2}\"", "OK"))
        if not ret:
            test.dut.at1.send_and_verify("at^spic")
            test.dut.at1.send_and_verify("at^spic?")

        test.expect(test.dut.at1.send_and_verify("AT+CPUC=\"EUR\",\"6.66\"", "OK"))
        # test.expect(test.dut.at1.send_and_verify("AT+CPUC?", ".*\+CPUC: \"EUR\",\"6.66\".*OK.*"))
        test.check_cpuc_read_resp(".*\+CPUC: \"EUR\",\"6.66\".*OK.*")
        pass

    def fd_pb_check(test):
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"FD\"", "OK"))
        test.expect(test.dut.dstl_write_pb_entries(3, '1234567890', '', 'PIN2check'))
        test.expect(test.dut.at1.send_and_verify('AT+CPBR=1,10', '.*\+CPBR: 3,"1234567890",.*,"PIN2check".*OK.*'))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=3", "OK"))
        pass

    def check_cpuc_read_resp(test, exp_resp):
        if test.dut.project is 'VIPER':
            test.expect(test.dut.at1.send_and_verify('at+cpuc?', '.*CME ERROR: unknown.*', timeout=25))
            test.log.warning("defect accepted by project, see VPR02-939")
            return True
        else:
            return test.expect(test.dut.at1.send_and_verify('at+cpuc?', exp_resp))


if "__main__" == __name__:
    unicorn.main()
