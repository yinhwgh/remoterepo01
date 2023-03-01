#responsible: baris.kildi@thalesgroup.com
#location: Berlin

import unicorn
import os, sys
import subprocess
from core.basetest import BaseTest

class Test(BaseTest):
    """ install all plugins which are already delivered
        like webimacs, junit, ssh...
    """

    def setup(test):
        pass

    def run(test):
        os.getcwd()
        current_dir = os.getcwd()
        test.log.info("Current dir: " + current_dir)
        test.log.info("To install desired plugin enter the plugin directory and call installation script")
        os.chdir("plugins")
        dirpath = os.getcwd()
        test.log.info("This is the location where all available plugins are stored: " + dirpath)

        available_plugins = ["junit", "ssh", "adb", "webimacs"]
        for plugin_name in available_plugins:
             os.chdir(plugin_name)
             test.log.info(f"Installation of {plugin_name} plugin was started")
             if ("win" in sys.platform):
             	   cmd = ".\install.cmd --proxy=http://10.50.101.10:3128"
             else:
                 cmd = "./install.sh --proxy=http://10.50.101.10:3128"

             process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
             output = process.communicate()[0]

             test.log.info(output)

             test.log.info("Installation of \"" + plugin_name + "\" plugin was finished successfully.")

             if ("Installation of \"" + plugin_name + "\" plugin was finished successfully." in output):
                  test.log.info("Plugin is properly installed and added into enabled.cfg")
                  test.expect("successfully" in output)
             else:
                  os.chdir("..")  # if it fails, go back in dirs. Otherwise other scripts will fail because base path is wrong
                  os.chdir("..")
                  raise Exception("Something went wrong please check your logfile")
             os.chdir("..")

        os.chdir("..")
        test.log.info("Test ends at this location: " + current_dir)



    def cleanup(test):
         pass


if "__main__" == __name__:
    unicorn.main()
