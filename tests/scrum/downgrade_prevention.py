#responsible: fang.liu@thalesgroup.com
#location: Berlin

import unicorn
import os
import re
import subprocess
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import *
from dstl.auxiliary.devboard.devboard import *
from dstl.auxiliary import init

class Test(BaseTest):

    def setup(test):
        """
        The precondition:
        Before the TC, please make sure the test swup files are prepared in advance;
        It should be produced with the tool MONO on linux.
        """
        test.dut.dstl_detect()

        test.log.info("The 1st precondition:\n"
                      "1.Before the TC, please make sure the test SWUP files are prepared in advance. It should be produced with the tool MONO on linux.\n"
                      "2.The base version of the test is started from FW90.\n")
        test.log.info("The 2nd precondition:\n"
                      "Please unlock the MSPC code and enable adb device.")

        '#Enable ADB interface'
        test.dut.at1.send_and_verify("At^scfg=\"serial/interface/adb\",enabled", ".*OK.*")

        '#Unlock the MSPC'
        test.dut.at1.send_and_verify("at^SCFG=\"security/passwd\",\"MSPC\",975004", ".*OK.*")

        '#Switch the adb device from "secure" mode to "root" mode.'
        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\",\"root\"", ".*OK.*")

        '#Make current running system as active system image.'
        test.dut.at1.send_and_verify("at^sfun=3", ".*OK.*")

        '#Restart module and to verify it\'s root mode.'
        test.dut.dstl_restart()

        '#Check if the ADB device is in root mode.'
        test.dut.at1.send_and_verify("AT^SCFG=\"Serial/Interface/Adb/Mode\"", ".*root.*")

    def run(test):

        """#Get current working directory"""
        global current
        current = os.path.dirname(os.path.realpath(__file__))
        print(current)

        "#Change the working directory to the folder which contains test swup files"
        global path
        path = os.path.abspath(os.path.join(current, "../../../"))

        global path_swupfiles
        path_swupfiles = os.path.dirname(os.path.join(path, "SWUP_files/"))
        print(path_swupfiles)

        test.log.info("%%%%%%Restart ADB device%%%%%%%%\n")
        os.system('adb kill-server')
        test.sleep(5)
        test.log.info('%%%%%Opening ADB device%%%%%%%')
        tmp = os.popen('adb devices -l').readlines()

        "#Filter all the devices' ID and then store in a list."
        pattern = '([a-zA-Z0-9]+)  +device'
        devices = []
        for line in tmp:
            searchObj = re.search(pattern, line)
            if searchObj:
                devices.append(searchObj.group(1))

        print("All the ADB devices are as follows:")
        print(devices)

        if len(devices) >= 1:
            test.log.info("%%%%%%Send a shell command to the module.%%%%%%")
            test.dut.adb.send_and_receive("hostname")
            test.expect("mdm" in test.dut.adb.last_response)
        else:
            test.log.error('It\'s failed to open ADB device, please check the device and environment again.')

        '#Compare the "meta.conf" files between the base version and intended FW version.'

        def base_version():

            test.dut.at1.send_and_verify("ati1", ".*OK.*")
            test.dut.at1.send_and_verify("ati3", ".*OK.*", append=True)
            test.dut.at1.send_and_verify("at^sos=bootloader/info", ".*OK.*", append=True)
            tmp = test.dut.at1.last_response
            print(tmp)
            dict = {'PRODUCT': '', 'BOOTLOADERVERSION': ' ', 'REVISION': [], 'A-REVISION': [], 'L-REVISION': []}

            searchObj = re.search('([a-zA-Z0-9]+)-([A-Z])', str(tmp))
            if searchObj:
                dict['PRODUCT'] = searchObj.group()
            else:
                test.log.error("Unknown Products.\n")
                raise Exception("Only BOBCAT 200 and PLPS9 Branch can support the function.\n")

            '#Collect all the values from command and store all revision values in dictionary.'
            pattern0 = 'SBL1_([0-9]+)'
            pattern1 = 'REVISION ([0-9]+).([0-9]+)'
            pattern2 = 'A-REVISION ([0-9]+).([0-9]+).([0-9]+)'
            pattern3 = 'L-REVISION ([0-9]+).([0-9]+).([0-9]+)'

            searchObj = re.search(pattern0, tmp)
            dict['BOOTLOADERVERSION'] = searchObj.group(1)

            searchObj = re.search(pattern1, tmp)
            dict['REVISION'].append(searchObj.group(1))
            dict['REVISION'].append(searchObj.group(2))

            searchObj = re.search(pattern2, tmp)
            dict['A-REVISION'].append(searchObj.group(1))
            dict['A-REVISION'].append(searchObj.group(2))
            dict['A-REVISION'].append(searchObj.group(3))

            searchObj = re.search(pattern3, tmp)
            dict['L-REVISION'].append(searchObj.group(1))
            dict['L-REVISION'].append(searchObj.group(2))
            dict['L-REVISION'].append(searchObj.group(3))

            return dict

        def new_version(path_folder, filename):
            """#Collect all the valuable values and store in the dictionary."""
            dict = {'PRODUCT': '', 'BOOTLOADERVERSION': ' ', 'REVISION': [], 'A-REVISION': [], 'L-REVISION': [],
                    'REVISION2': [], 'AREVISION2': []}
            swup_file = open(path_folder + "/" + filename, 'r')
            content = swup_file.read()
            searchObj = re.search('([a-zA-Z0-9]+)-([A-Z])-([0-9]+)', content)
            if searchObj:
                dict['PRODUCT'] = searchObj.group()
            else:
                test.log.error("Unknown Products.\n")
                raise Exception("Only BOBCAT 200 and PLPS9 Branch can support the function.\n")

            '#Collect all the values from command and store all revision values in dictionary.'
            pattern0 = 'BOOTLOADERVERSION=([0-9]+)'
            pattern1 = 'REVISION=([0-9]+).([0-9]+)'
            pattern2 = 'AREVISION=([0-9]+).([0-9]+).([0-9]+)'
            pattern3 = 'LREVISION=([0-9]+).([0-9]+).([0-9]+)'
            pattern4 = 'REVISION2=([0-9]+).([0-9]+)'
            pattern5 = 'AREVISION2=([0-9]+).([0-9]+).([0-9]+)'

            searchObj = re.search(pattern0, content)
            if searchObj:
                dict['BOOTLOADERVERSION'] = searchObj.group(1)
            else:
                test.log.info("No bootloader item in the \"meta.conf\" file.\n")

            searchObj = re.search(pattern1, content)
            dict['REVISION'].append(searchObj.group(1))
            dict['REVISION'].append(searchObj.group(2))

            searchObj = re.search(pattern2, content)
            dict['A-REVISION'].append(searchObj.group(1))
            dict['A-REVISION'].append(searchObj.group(2))
            dict['A-REVISION'].append(searchObj.group(3))

            searchObj = re.search(pattern3, content)
            dict['L-REVISION'].append(searchObj.group(1))
            dict['L-REVISION'].append(searchObj.group(2))
            dict['L-REVISION'].append(searchObj.group(3))

            searchObj = re.search(pattern4, content)
            if searchObj:
                dict['REVISION2'].append(searchObj.group(1))
                dict['REVISION2'].append(searchObj.group(2))

            searchObj = re.search(pattern5, content)
            if searchObj:
                dict['AREVISION2'].append(searchObj.group(1))
                dict['AREVISION2'].append(searchObj.group(2))
                dict['AREVISION2'].append(searchObj.group(3))

            swup_file.close()
            return dict

        def compare_Result(dic_base, dic_new):
            global res
            res = True
            for x, i in zip(dic_base['REVISION'], dic_new['REVISION']):
                if int(x) > int(i):
                    res = False
                    return res
                else:
                    continue

            for x, i in zip(dic_base['BOOTLOADERVERSION'], dic_new['BOOTLOADERVERSION']):
                if i is not ' ':
                    if int(x) > int(i):
                        res = False
                        return res
                else:
                    continue

            for x, i in zip(dic_base['A-REVISION'], dic_new['A-REVISION']):
                if int(x) > int(i):
                    res = False
                    return res
                else:
                    continue

            for x, i in zip(dic_base['L-REVISION'], dic_new['L-REVISION']):
                if int(x) > int(i):
                    res = False
                    return res
                else:
                    continue

        def update_FW():
            """Get all the test swup files and meta files in the folder, which contains all the test swup files."""
            os.chdir(path_swupfiles)
            p_list = os.listdir(path_swupfiles)
            pattern_swup = '.*(test.*.usf)'
            pattern_meta = '.*(meta.*.config)'
            file_list_swup = []
            file_list_meta = []
            for line in p_list:
                search_Obj1 = re.search(pattern_swup, line)
                search_Obj2 = re.search(pattern_meta, line)
                if search_Obj1:
                    test_swup = search_Obj1.group(0)
                    file_list_swup.append(test_swup)

                elif search_Obj2:
                    meta_file = search_Obj2.group(1)
                    file_list_meta.append(meta_file)

                else:
                    continue

            test.log.info("All the revision values of base version on the module.\n")
            dict1 = base_version()
            for key, values in dict1.items():
                print(key, values)

            '#List all the swup and meta files in the current folder.'
            '#Get all the expected results for each each swup files.'
            exp_result = []
            print(file_list_meta)
            print(file_list_swup)
            for meta_files in file_list_meta:
                test.log.info("%%%%%Print out all the values of {}.%%%%%\n".format(meta_files))
                dict2 = new_version(path_swupfiles, meta_files)
                for key, values in dict2.items():
                    print(key, values)
                exp_result.append(compare_Result(dict1, dict2))

            test.log.info("The list of all the expect results after comparision.\n")
            print(exp_result)

            """Update module with all the test swup files that are available."""
            actualResult = []
            counter = 0
            for item in file_list_swup:
                '#Update swup file to the module.'
                cmd = 'adb push {} /tmp/test.usf'.format(item)
                result = subprocess.getoutput(cmd)
                test.log.info("The result of \"adb push ...\".\n")
                print(result)
                '#Check the result code after finished swup updating'
                cmd = "adb shell \"swup -u /tmp/test.usf\""
                subprocess.getoutput(cmd)
                test.log.info("The result of \"adb shell swup...\".\n")

                cmd = "adb shell \"swup -u /tmp/test.usf;echo Return:$?\""
                returnCode = subprocess.getoutput(cmd)
                print(returnCode)
                searchObjCode = re.search("Return:([0-9])", returnCode)

                cmd = "adb shell \"dmesg|grep swup\""
                if searchObjCode:
                    resultCode = searchObjCode.group(1)
                    test.log.info("The result code of swup is {}.".format(resultCode))
                    if resultCode == 0:
                        actualResult.append(True)
                        if exp_result[counter] == actualResult[counter]:
                            test.expect(True)
                        else:
                            test.expect(False)
                    else:
                        actualResult.append(False)
                        '#Check the output from kernel'
                        test.log.info("Check the result from kernel log.\n")
                        result = subprocess.getoutput(cmd)
                        print(result)
                        pattern_validation = "Validation [23]"
                        search_Obj = re.search(pattern_validation, result)
                        if search_Obj:
                            test.log.info("The feature Downgrade prevention has taken effect!\n")
                            if exp_result[counter] == actualResult[counter]:
                                test.expect(True)
                            else:
                                test.expect(False)
                else:
                    continue
                counter = counter + 1

        update_FW()

        """Change directory to the default directory "..../tests/scrum/"""""
        os.chdir(current)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
