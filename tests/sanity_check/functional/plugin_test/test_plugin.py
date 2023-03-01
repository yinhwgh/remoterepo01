#responsible: baris.kildi@thalesgroup.com
#location: Berlin

import unicorn
import os
import subprocess
from core.basetest import BaseTest

class Test(BaseTest):
    """ To enable the plugin open enabled.cfg file and write into all needed plugin names
    like webimacs, junit, ...
    """

    def setup(test):
        pass

    def run(test):
        os.getcwd()
        current_dir = os.getcwd()
        test.log.info("Here we are " + current_dir)
        os.chdir("plugins")
        file = open("enabled.cfg", 'w')
        file.write("## add enabled plugins here - each in separate line\nwebimacs\njunit\ntemplate")
        file = open("enabled.cfg", 'r')
        contents = file.read()
        if ("webimacs" in contents):
            test.log.info("Webimacs plugin is properly added into enabled.cfg")
            test.expect("webimacs" in contents)
            #return True
        else:
            raise Exception("Something went wrong please check your logfile")
        file.close()


        test.log.info("Delete the whole content of simdata.cfg file")
        #os.chdir("..\config")
        os.chdir(os.path.join("..", "config"))
        file = open("simdata.cfg", 'w')
        file.close()
        os.chdir(os.path.join(".."))
        os.getcwd()
        current_dir = os.getcwd()
        test.log.info("Here we are " + current_dir)


        """
        os.chdir("..")
        dirpath = os.getcwd()
        test.log.info("Your current directory is : " + dirpath)
        myCmd = (
            'python\\python.exe unicorn.py tests\\sanity_check\\plugin_test\\test_plugin_2.py -l config\\local.cfg')
        subprocess.call(myCmd, shell='TRUE')
        os.chdir("config")
        file = open("simdata.cfg", 'r')
        contents = file.read()
        if ("pin1" in contents):
            test.log.info("config/simdata.cfg file is automatically filled based on entries from WebImacs")
            test.expect("pin1" in contents)
        else:
            raise Exception("Something went wrong please check your WebImacs plugin")
        file.close()
        """

    def cleanup(test):
         pass


if "__main__" == __name__:
    unicorn.main()
