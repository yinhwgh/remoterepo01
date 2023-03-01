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
        file = open("enabled.cfg", 'w')
        file.write("## add enabled plugins here - each in separate line\nwebimacs\njunit\ntemplate\nssh")
        file = open("enabled.cfg", 'r')
        contents = file.read()
        if ("webimacs" in contents):
            test.log.info("Webimacs plugin is properly added into enabled.cfg")
            test.expect("webimacs" in contents)
            #return True
        else:
            raise Exception("Something went wrong please check your logfile")
        file.close()


    def cleanup(test):
         pass


if "__main__" == __name__:
    unicorn.main()
