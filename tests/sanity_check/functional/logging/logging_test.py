#responsible: johann.suhr@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
import os, re
from pathlib import Path

from dstl.auxiliary import init

class Test(BaseTest):
    """ Test logging methods. """

    def setup(test):
        test.dut.dstl_detect()
        pass

    def run(test):

        test_msg = "Houston, we have a problem"

        test.log.com(test_msg)
        test.log.info(test_msg)
        test.log.warn(test_msg)
        test.log.error(test_msg)
        test.log.critical(test_msg)
        test.log.debug(test_msg)

        test_msg = "Houston, we have a %s"
        test_log_arg = "major problem"

        test.log.com(test_msg, test_log_arg)
        test.log.info(test_msg, test_log_arg)
        test.log.warn(test_msg, test_log_arg)
        test.log.error(test_msg, test_log_arg)
        test.log.critical(test_msg, test_log_arg)
        test.log.debug(test_msg, test_log_arg)

        expected = [
            r'Houston, we have a problem',
            r'INFO    : Houston, we have a problem',
            r'WARNING : Houston, we have a problem',
            r'ERROR   : Houston, we have a problem',
            r'CRITICAL: Houston, we have a problem',
            r'DEBUG   : Houston, we have a problem',
            r'Houston, we have a major problem',
            r'INFO    : Houston, we have a major problem',
            r'WARNING : Houston, we have a major problem',
            r'ERROR   : Houston, we have a major problem',
            r'CRITICAL: Houston, we have a major problem',
            r'DEBUG   : Houston, we have a major problem'
        ]

        # Get the path of log directory.
        current_dir = os.getcwd()
        test.log.info("Current dir: " + current_dir)
        #base_path = current_dir[:current_dir.find("unicorn\\tests") + len("unicorn")]
        base_path = current_dir
        test.log.info("Base path: " + base_path)
        #log_dir =  r'' + base_path + r"\logs"
        log_dir = os.path.join(base_path, "logs")   # adaption for Linux
        test.log.info("Log dir: " + log_dir)

        # Get the path of the latest log file.
        latest_file = sorted([filename for filename in Path(log_dir).glob('**/*logging_test*_test.log')],
                             key=os.path.getmtime, reverse=True)[0]

        # Append every occurence of expected in latest_file to matches.
        matches = []
        with open(latest_file) as file:
            lines = file.readlines()
            for test_msg in expected:
                for line in lines:
                    pattern = "^\\d{4}[-]?\\d{1,2}[-]?\\d{1,2} \\d{1,2}:\\d{1,2}:\\d{1,2}[,]?\\d{1,3} " + test_msg
                    match = re.findall(pattern, line)
                    if match:
                        matches.append(match)
                        test.log.info("Found in log file: " + str(match))

        # The length of matches and expected should be equal.
        test.expect(len(matches) == len(expected))


    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
