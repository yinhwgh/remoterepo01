#responsible: fang.liu@thalesgroup.com
#location: Berlin

import unicorn
import os
from subprocess import Popen, PIPE
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import *
from dstl.auxiliary.devboard.devboard import *
from dstl.auxiliary import init

class Test(BaseTest):
    """ Test example for devboard DSTL methods for Bobcat step 2"""

    def setup(test):

        test.dut.at1.send_and_verify("at^cicret=swn", ".*OK.*")

        test.log.info("The preconditions: \n"
                      "1. Firstly, please copy the folder of NV tools, which is the same folder level with unicorn project;\n"
                      "2. Try to read a NV block item first;\n"
                      "3. Write NV image into the module, and make sure the image file is in that location in advance.\n"
                      "4. Totally, there are 9 checkpoints, the script have to assure all these checkpoints have to be checked.\n"
                      "5. Currently, the USB4 is hardcoded, you have to change the port whenever it's necessary.\n"
                      )
        test.dut.dstl_detect()

        current = os.path.dirname(os.path.realpath(__file__))

        test.log.info("1st: The current directory is :{}".format(current))
        test.log.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                      "      1. Change working directory to the NV tool.\n"
                      "      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")

        path = os.path.abspath(os.path.join(current, "../../../"))
        nv_tool_dir = os.path.dirname(os.path.join(path, "NV_tools/qnvitem.exe"))

        test.log.info("2nd: The current directory is :{}".format(nv_tool_dir))

        '#Check if the tool "qnvitem.exe" existed in the directory."'
        if os.path.isfile(os.path.join(nv_tool_dir, "qnvitem.exe")):
            test.log.info("The tool exists in the directory.\n")
            test.expect(True)
        else:
            raise Exception("The tool does not exit in the directory.\n")

    def run(test):

        """#Activate "qnvitem.exe" via command line."""
        test.log.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                      "      2. Open the NV tool and read one NV block of the DUT via diagnostic port.\n"
                      "      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        current = os.path.dirname(os.path.realpath(__file__))
        path = os.path.abspath(os.path.join(current, "../../../"))
        nv_tool_dir = os.path.join(path, "NV_tools")
        qnvitem_tool = os.path.join(nv_tool_dir, "qnvitem.exe")

        print(current)
        print(nv_tool_dir)
        print(qnvitem_tool)

        os.chdir(nv_tool_dir)

        p = Popen(qnvitem_tool, stdin=None, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()

        out = out.decode('gbk')
        err = err.decode('gbk')

        print("output:\n" + out)
        print("Error:\n" + err)

        expStr = "version 1.0"

        '#Check if the tool "qnvitem.exe" is actived or not, and how to deal with it when it\'s not actived.'
        if expStr in err:
            test.log.info("The tool \"qnvitem.exe\" is actived now.\n")
            test.expect(expStr in err)
        else:
            raise Exception("The tool \"qnvitem.exe\" is not available now.\n")
        p.kill()
        test.sleep(5)

        '#Read value from NV block, such as 50315 from current module.'
        test.log.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                      "      3. Read one NV block as 50315 from current module before FTM;\n"
                      "         The value of DATA_BYTES should be 0x09 or 0x00 before FTM.\n"
                      "      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        rc = Popen(qnvitem_tool + " -v -p 20 -r 50315", stdin=None, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = rc.communicate()

        out = out.decode('gbk')
        err = err.decode('gbk')

        test.expect("0x09" in out or "0x00" in out or "0x0a" in out)

        print("Output:\n" + out)
        print("Error:\n" + err)
        rc.kill()
        test.sleep(5)

        test.log.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                      "      4. Write NV image into the module, and then check if the NV image has been written successfully.\n"
                      "      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        rc = Popen(qnvitem_tool + " -v -p 20 -w 20190724162134_test_self_control_band5.txt", stdin=None, stdout=PIPE,
                   stderr=PIPE, shell=True)
        out, err = rc.communicate()

        out = out.decode('gbk')
        err = err.decode('gbk')

        print("Output:\n" + out)
        print("Error:\n" + err)

        errlines = err.splitlines()
        counter = 0
        for line in errlines:
            if "done" in line:
                counter = counter + 1
        test.expect(counter == 16)
        rc.kill()
        test.sleep(5)

        test.log.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                      "      5. Enable FTM of DUT and check if module will shutdown after self testing procedures.\n"
                      "      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        test.dut.at1.send_and_verify("at+cfun=5", ".*OK.*")
        test.dut.at1.send_and_verify("at^smso", ".*OK.*")
        test.sleep(10)
        test.dut.devboard.send_and_verify("mc:igt=3000")

        test.log.info("%%%%%%%%%%%%%%%%%%%%%\n"
                      "      Module is in FTM now.\n"
                      "      %%%%%%%%%%%%%%%%%%%%%")
        test.sleep(100)

        '#Check if the devboard is switched off'
        result = test.dut.dstl_check_if_module_is_on_via_dev_board()

        if not result:
            test.expect(True)
            test.log.info("Module is switched off after FTM.\n")
        else:
            test.log.error("Module is not switched off after FTM.\n")

        '#Read value from NV block, such as 50315 from current module.'
        test.log.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                      "      6. Read one NV block as 50315 from current module after FTM,\n"
                      "      The value of DATA_BYTES should be 0x0a after FTM.\n"
                      "      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        test.dut.devboard.send_and_verify("mc:vbatt=on")
        test.dut.devboard.send_and_verify("mc:igt=3000")
        test.sleep(60)
        test.dut.at1.send_and_verify("at", ".*OK.*")

        rc = Popen(qnvitem_tool + " -v -p 20 -r 50315", stdin=None, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = rc.communicate()

        out = out.decode('gbk')
        err = err.decode('gbk')

        test.log.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                      "     7. Check if the FTM have taken effect.\n"
                      "      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        test.expect("0x0a" in out)
        print("The output information from NV block is:\n" + out)
        print("The other information from NV block is:\n" + err)
        rc.kill()

        test.log.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                      "      8. Turn the module back to normal full functionality mode.\n"
                      "      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        rc = Popen(qnvitem_tool + " -v -p 20 -w Return_normal_mode_453.nv", stdin=None, stdout=PIPE,
                   stderr=PIPE, shell=True)
        out, err = rc.communicate(10)

        out = out.decode('gbk')
        err = err.decode('gbk')

        print("Output:\n" + out)
        print("Error:\n" + err)

        test.expect("done" in err)

        if "done" in err:
            test.dut.dstl_restart()
        else:
            raise Exception("Error: module return back to normal mode failed.\n")

        '#The last step to check if module have turn back to full functionality mode.'
        test.log.info("Read the NV block 453 from the module, the DATA_BYTE should be 0x00.\n")
        rc = Popen("qnvitem.exe -v -p 20 -r 453", stdin=None, stdout=PIPE,
                   stderr=PIPE, shell=True)

        out, err = rc.communicate(10)

        out = out.decode('gbk')
        err = err.decode('gbk')

        print("Output:\n" + out)
        print("Error:\n" + err)
        test.expect("0x00" in out)

        rc.kill()

        test.dut.at1.send_and_verify("at+cfun?", ".*OK.*")
        if "1" in test.dut.at1.last_response or "4" in test.dut.at1.last_response:
            test.expect(True)
        else:
            test.log.error("Module is not in normal mode (full functionality is 1, airplane mode is 4).\n")

        os.chdir(current)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

