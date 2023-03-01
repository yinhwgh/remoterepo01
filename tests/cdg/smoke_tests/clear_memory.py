#responsible agata.mastalska@globallogic.com
#Wroclaw

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service import register_to_network
import re


class Test(BaseTest):
    """
    Clear memory
    Stop and remove all MIDlets except SLAE and JRC or from 'do_not_delete' list
    Clear all files from MES except files and folders from 'do_not_delete' list

    1. Stop and remove all MIDlets
    2. Delete all non restricted files and folders

    author: agata.mastalska@globallogic.com
    """

    def setup(test):
        test.dut.dstl_detect()

    #@property
    def run(test):
        test.log.step("Clear memory")
        restricted_list = ["SLAE", "JRC"] + test.do_not_delete
        module_with_midlet = ["JAKARTA", "BOXWOOD", "GINGER", "ODESSA"]
        if test.dut.project not in module_with_midlet:
            test.log.info("Module without MIDlets")
            return test.expect(True)

        test.log.step("1. Stop and remove all MIDlets")
        list_of_midlets = get_list_of_midlets(test)
        dont_remove = [midlet for midlet in list_of_midlets \
            if any(dont_remove_midlet in midlet for dont_remove_midlet in restricted_list)]

        for midlet in list_of_midlets:
            if midlet not in dont_remove:
                test.expect(test.dut.at1.send_and_verify('AT^SJAM=2,{},""'.format(midlet), '.*OK.*'))
                test.log.info("Stopped {}".format(midlet))
                test.expect(test.dut.at1.send_and_verify('AT^SJAM=3,{},""'.format(midlet), '.*OK.*'))
                test.log.info("Removed {}".format(midlet))
            else:
                test.log.info("No removed. Midlet on restricted list {}".format(midlet))

        test.log.step("2. Delete all non restricted files and folders")
        list_of_folders = get_folders_as_list(test, folder_path="")
        list_of_files = get_files_as_list(test, folder_path="")

        dont_remove = [single_file for single_file in list_of_files \
            if any(dont_remove_file in single_file for dont_remove_file in restricted_list)]

        for single_file in list_of_files:
            test.log.info("Try to delete: {}".format(single_file))
            if single_file not in dont_remove:
                test.log.info("Remove: {}".format(single_file))
                test.expect(test.dut.at1.send_and_verify('AT^SFSA="remove","a:/{}"'.format(single_file)))
            else:
                test.log.info("File on restricted list: {}".format(single_file))

        dont_remove = [folder for folder in list_of_folders \
            if any(dont_remove_folder in folder for dont_remove_folder in restricted_list)]

        for folder in list_of_folders:
            test.log.info("Try to delete : {}".format(folder))
            if folder not in dont_remove:
                test.log.info("Remove: {}".format(folder))
                test.expect(test.dut.at1.send_and_verify('AT^SFSA="rmdir","a:/{}"'.format(folder)))
            else:
                test.log.info("Folder on restricted list: {}".format(folder))

    def cleanup(test):
        test.dut.at1.close()

if "__main__" == __name__:
    unicorn.main()

def get_list_of_midlets(test):
    test.expect(test.dut.at1.send_and_verify('AT^SJAM=4', '.*OK.*'))
    split_response = test.dut.at1.last_response.split("\n")
    while("" in split_response):
        split_response.remove("")
    list_of_midlets = []
    for middlet in split_response:
        pattern = re.compile(r'\"(.+.jad)\"')
        result = pattern.search(middlet)
        if result:
            list_of_midlets.append(result.group(0))
    return list_of_midlets

def get_folders_as_list(test, folder_path=""):
    test.dut.at1.send_and_verify("AT^SFSA=\"ls\",\"a:/{}\"".format(folder_path), "^SFSA: 0")
    files_list_str = test.dut.at1.last_response
    regrex = re.findall("(\^SFSA: \"([a-zA-Z0-9_\-() ]*[/])\")", files_list_str)
    files_list = []
    for element in regrex:
        files_list.append(element[1])
    return files_list

def get_files_as_list(test, folder_path=""):
    test.dut.at1.send_and_verify("AT^SFSA=\"ls\",\"a:/{}\"".format(folder_path), "^SFSA: 0")
    files_list_str = test.dut.at1.last_response
    regrex = re.findall("(\^SFSA: \"([a-zA-Z0-9_\-() ]*\.\w+)\")\s*\n", files_list_str)
    files_list = []
    for element in regrex:
        files_list.append(element[1])
    return files_list
