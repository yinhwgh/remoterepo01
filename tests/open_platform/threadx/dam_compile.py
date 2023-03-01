import os
import unicorn
import time

from core.basetest import BaseTest
import dstl.embedded_system.embedded_system_configuration
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.auxiliary import restart_module


class Test(BaseTest):
    """
    Test which presents basic use of DSTL functions
    """

    def setup(test):
        pass

    def run(test):
        app_path = "C:\c_project\Embeded\myFiles\ep_tcpclient_duration\ep_tcpclient_duration"

        port = "COM6"
        is_secure = True

        # Compile dam application
        index = app_path.rindex("\\")
        app_dir = app_path[0:index]
        app_name = app_path[index + 1:]

        bat_cmd = "build_scripts\\build.bat -p exs_tx {} {}".format(app_dir, app_name)
        print(bat_cmd)
        os.system(bat_cmd)

        # Sign application
        application_path = "build\\{}\\{}.bin".format(app_name, app_name)
        if is_secure:
            bat_cmd = "app.py sign --key build_scripts\\app_rot.key {}".format(application_path)
            print(bat_cmd)
            os.system(bat_cmd)
            application_path = "build\\{}\\signed\\{}.bin".format(app_name, app_name)

        # Upload application to device
        bat_cmd = "connect.py -p {} -s 115200".format(port)
        print(bat_cmd)
        os.system(bat_cmd)

        bat_cmd = "app.py download -e {}".format(application_path)
        print(bat_cmd)
        os.system(bat_cmd)


    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()



