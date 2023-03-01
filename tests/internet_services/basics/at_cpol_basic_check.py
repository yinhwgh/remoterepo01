# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0091863.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
import dstl.usim.get_imsi
from dstl.identification.collect_module_infos import dstl_collect_module_info


class Test(BaseTest):

    cpol_format = '0-2'
    without_eutran = False
    with_cpls = True

    def setup(test):
        test.default_setting = None
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_lock_sim()
        test.dut.dstl_get_imsi()

        global cpol_format
        global without_eutran
        global with_cpls
        with_cpls = False
        if test.dut.platform == 'XGOLD':
            without_eutran = True
            cpol_format = '2'
            exp_resp_cpls = ".*ERROR.*"     # this ATC does not exit on old products

        if with_cpls:
            test.expect(test.dut.at1.send_and_verify("AT+CPLS?", ".*\+CPLS: 0.*OK.*"))  # power up value!
        test.dut.dstl_restart()

    def run(test):
        test.log.info("1. Test: test and exec command without pin authentication.")
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL=?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL=9", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL", ".*ERROR.*"))

        test.log.info("2. Test: test and exec command with pin authentication.")
        test.expect(test.dut.dstl_enter_pin())
        test.attempt(test.dut.at1.send_and_verify, "AT+CPIN?", expect="READY", sleep=1, retry=2)
        test.attempt(test.dut.at1.send_and_verify, "AT+CPOL?", expect=".*OK.*", sleep=1, retry=3)
        test.expect(test.dut.at1.send_and_verify("AT+CPOL", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", ".*OK.*"))
        test.sleep(2)
        global cpol_format
        max_cpol_index = test.get_max_cpol_index()
        test.expect(test.dut.at1.send_and_verify("AT+CPOL=?",
                                                 f".*\\+CPOL: \\(1-{max_cpol_index}\\),\\({cpol_format}\\).*OK.*"))

        test.log.step("3. Test: test with added parameter or invalid command .")
        test.expect(test.dut.at1.send_and_verify("AT+CPOL={},2,\"33210\"".format(int(max_cpol_index) + 1), ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL={},1,\"43333\"".format(int(max_cpol_index) - 1), ".*ERROR.*"))

        test.log.info("4. Functionality test.")
        test.log.step("4.1 Save the default setting.")
        test.save_default_setting()

        test.log.step("4.2 Delete all settings.")
        for i in range(max_cpol_index):
            test.expect(test.dut.at1.send_and_verify("AT+CPOL={}".format(i + 1), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", ".*CPOL\\?\\s*OK\\s*"))

        test.log.step("4.3 Write some settings.")
        global without_eutran
        for i in range(6):
            if without_eutran:
                test.expect(test.dut.at1.send_and_verify('AT+CPOL={},2,"2340{}",{},0,{}'
                                                         .format(i + 1, i + 1, i % 2, 1 - i % 2), ".*OK.*"))
            else:
                test.expect(test.dut.at1.send_and_verify('AT+CPOL={},2,"2340{}",{},0,{},{}'
                                                         .format(i + 1, i + 1, i % 2, 1 - i % 2, i % 2), ".*OK.*"))

        test.expect(test.dut.at1.send_and_verify('AT+CPOL={},2,"33333"'.format(max_cpol_index), ".*OK.*"))

        expected_response = ".*" \
                            "\\+CPOL: 1,2,\"23401\",0,0,1,0\\s*" \
                            "\\+CPOL: 2,2,\"23402\",1,0,0,1\\s*" \
                            "\\+CPOL: 3,2,\"23403\",0,0,1,0\\s*" \
                            "\\+CPOL: 4,2,\"23404\",1,0,0,1\\s*" \
                            "\\+CPOL: 5,2,\"23405\",0,0,1,0\\s*" \
                            "\\+CPOL: 6,2,\"23406\",1,0,0,1\\s*" \
                            "\\+CPOL: {},2,\"33333\",(0|1),0,(0|1),(0|1)\\s*" \
                            "\\s*OK\\s*".format(max_cpol_index)

        if without_eutran:
            expected_response = ".*" \
                                "\\+CPOL: 1,2,\"23401\",0,0,1\\s*" \
                                "\\+CPOL: 2,2,\"23402\",1,0,0\\s*" \
                                "\\+CPOL: 3,2,\"23403\",0,0,1\\s*" \
                                "\\+CPOL: 4,2,\"23404\",1,0,0\\s*" \
                                "\\+CPOL: 5,2,\"23405\",0,0,1\\s*" \
                                "\\+CPOL: 6,2,\"23406\",1,0,0\\s*" \
                                "\\+CPOL: {},2,\"33333\",(0|1),0,(0|1)\\s*" \
                                "\\s*OK\\s*".format(max_cpol_index)

        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", expected_response))

        test.expect(test.dut.at1.send_and_verify("AT+CPOL={},2,\"33210\"".format(int(max_cpol_index) + 1), ".*ERROR.*"))

        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", expected_response))

        test.expect(test.dut.at1.send_and_verify("AT+CPOL=5", ".*OK.*"))

        expected_response = ".*" \
                            "\\+CPOL: 1,2,\"23401\",0,0,1,0\\s*" \
                            "\\+CPOL: 2,2,\"23402\",1,0,0,1\\s*" \
                            "\\+CPOL: 3,2,\"23403\",0,0,1,0\\s*" \
                            "\\+CPOL: 4,2,\"23404\",1,0,0,1\\s*" \
                            "\\+CPOL: 6,2,\"23406\",1,0,0,1\\s*" \
                            "\\+CPOL: {},2,\"33333\",(0|1),0,(0|1),(0|1)\\s*" \
                            "\\s*OK\\s*".format(max_cpol_index)
        if without_eutran:
            expected_response = ".*" \
                                "\\+CPOL: 1,2,\"23401\",0,0,1\\s*" \
                                "\\+CPOL: 2,2,\"23402\",1,0,0\\s*" \
                                "\\+CPOL: 3,2,\"23403\",0,0,1\\s*" \
                                "\\+CPOL: 4,2,\"23404\",1,0,0\\s*" \
                                "\\+CPOL: 6,2,\"23406\",1,0,0\\s*" \
                                "\\+CPOL: {},2,\"33333\",(0|1),0,(0|1)\\s*" \
                                "\\s*OK\\s*".format(max_cpol_index)

        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", expected_response))

        test.log.info("4.4 Delete the settings.")
        for i in range(6):
            test.expect(test.dut.at1.send_and_verify('AT+CPOL={}'.format(i + 1), ".*OK.*"))

        test.expect(test.dut.at1.send_and_verify("AT+CPOL={}".format(max_cpol_index), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", ".*CPOL\\?\\s*OK\\s*"))

        global with_cpls
        if with_cpls:
            test.log.step("5. negative test with +CPLS=1 or =2")
            test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))
            operation_error = "\+CME ERROR: operation not allowed"
            index_error = "\+CME ERROR: invalid index"
            for i in range(1, 3):
                test.expect(test.dut.at1.send_and_verify(f"AT+CPLS={i}", "OK"))
                test.expect(test.dut.at1.send_and_verify("AT+CPOL?", "OK"))
                # write error
                test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=1,2,\"12000\"", operation_error))
                # invalid parameter error
                test.expect(test.dut.at1.send_and_verify("AT+CPOL=100,2,\"46000\",", index_error))
                # delete error
                test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=1", operation_error))
        else:
            test.log.step("5. negative test with +CPLS=x overjumped - product does not support +CPLS")

        pass

    def get_max_cpol_index(test):
        test.expect(test.dut.at1.send_and_verify("AT+CPOL=?", ".*OK.*"))
        start_index = test.dut.at1.last_response.index("(")
        end_index = test.dut.at1.last_response.index(")")
        print(type(start_index))
        print(type(test.dut.at1.last_response))

        if 0 < start_index < end_index:
            string1 = test.dut.at1.last_response[start_index + 1: end_index]
            items = string1.split("-")
            if len(items) == 2:
                return int(items[1])

        return -1

    def save_default_setting(test):
        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", ".*OK.*"))
        test.default_setting = test.dut.at1.last_response

        # print("last reponse: ")
        # print(test.dut.at1.last_response)
        # print("read: ")
        # print(test.dut.at1.read())

        test.default_setting = test.default_setting.replace("AT+CPOL", "").replace("OK", "").strip()
        # print("default setting: ")
        # print(test.default_setting)

    def restore_default_setting(test):
        if test.default_setting:
            for line in test.default_setting.split("+CPOL:"):
                line = line.strip()
                print(line)
                test.expect(test.dut.at1.send_and_verify("AT+CPOL={}".format(line), ".*OK.*"))

    def cleanup(test):
        test.log.info("Restore default settings.")
        global with_cpls
        if with_cpls:
            test.expect(test.dut.at1.send_and_verify("AT+CPLS=0", "OK"))
        test.restore_default_setting()
        # test.dut.dstl_restart()


if "__main__" == __name__:
    unicorn.main()