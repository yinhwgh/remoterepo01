#responsible: baris.kildi@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
import sys
import os
import re
import glob
from pathlib import Path
import subprocess
from dstl.network_service import register_to_network
from dstl.auxiliary import tracing


DEFAULT_PROXY_BLN = "http://10.50.101.10:3128"


class Test(BaseTest):
    """ Prepare unicorn to capture qxdm trace by installing tracing plugin.
        Check if tracing is enabled 
        
        to run without proxy or to override its value: 
        
        unicorn qxdm_prepare.py --proxy=None
        """

    def setup(test):
        
        test.require_parameter("proxy", default=DEFAULT_PROXY_BLN)
       
        test.proxy_address = test.proxy

        test.log.info("Using proxy address: {}".format(test.proxy_address))
        test.unicorn_dir = os.path.abspath(os.path.dirname(unicorn.__file__))
        test.plugins_dir = os.path.join(test.unicorn_dir, "plugins")


    def run(test):
        
        test.log.info("Unicorn dir: {}".format(test.unicorn_dir))
        test.log.info("To install desired plugin enter the plugin directory and call installation script")
        test.log.info("This is the location where all available plugins are stored: {}".format(test.plugins_dir))
        
        test.log.step("Install tracing plugin")
        
        available_plugins = ["tracing"]
        
        for plugin_name in available_plugins:
            plugin_dir = os.path.join(test.plugins_dir, plugin_name)
            os.chdir(test.plugins_dir)
            dirpath = os.getcwd()
            test.log.info("Starting installation of \"{}\" plugin in {}".format(plugin_name, dirpath))
            cmd = ""
            if ("win" in sys.platform):
                cmd = "install.cmd {}".format(plugin_name)
            else:
                cmd = "./install.sh {}".format(plugin_name)
            if test.proxy_address:
                cmd = cmd + " --proxy={}".format(test.proxy_address)
        
            output = test.os.execute(cmd, shell=False)
            # process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
            # output = process.communicate()[0]        
        
            if (("Installation of \"" + plugin_name + "\" plugin was finished successfully.") in output):
                test.log.info("Tracing plugin is properly installed")
                test.expect("successfully" in output)
            else:
                os.chdir(test.unicorn_dir)
                test.expect(False, msg="Something went wrong please check your logfile") 

        enabled_plugins_cfg = os.path.join(test.plugins_dir, "enabled.cfg")
        os.chdir(test.unicorn_dir)
        with open(enabled_plugins_cfg, 'r') as f:
        
            for plugin_name in available_plugins:    
                test.log.step("Check if {} plugin is added into enabled.cfg file".format(plugin_name))
            
                lines = f.read().strip().split()
                if plugin_name in lines:
                    test.log.info("{} plugin is successfully added into enabled.cfg".format(plugin_name))
                    test.expect(plugin_name in lines)
                else:
                    test.log.error("{} is somehow not enabled".format(plugin_name))
                    test.expect(False)


    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
