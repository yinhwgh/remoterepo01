# responsible: karsten.labuske@thalesgroup.com
# location: Berlin
# Test case: UNISIM01-355

import unicorn
import os
from core.basetest import BaseTest
from pathlib import Path

testkey = "UNISIM01-355"


class Test(BaseTest):
    """
    AT cmd list from DSTL and Test Cases
    """

    def setup(test):
        global out_file
        global log_fd
        global at_dict

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')

        base = str(os.path.realpath(__file__))
        base = base[0:base.rfind("unicorn\\")+len("unicorn\\")]
        test.log.info('Base directory: ' + base)

        test.require_parameter('base_dir', default=base)
        test.require_parameter('file_pattern', default='mods_e2e_unicorn')
        test.require_parameter('keyword1', default='send_and_verify')
        test.require_parameter('keyword2', default='send_and_verify_retry')


        # output file
        out_file = "mods_e2e_unicorn_used_at_commands.txt"
        log_fd = open(out_file, "w")
        test.log.info("Output file: " + out_file)

        # AT cmd dictionary
        at_dict = {}

    @staticmethod
    def parse_path(test, path, keyword1, keyword2, pattern, ftype):
        test.log.info("Searching path: " + path + " for keyword " + keyword1 + " [file pattern " + pattern + "]")

        files = []
        ctr = 0

        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if '.py' in file and pattern in file and not '.pyc' in file:
                    files.append(os.path.join(r, file))

        for f in files:
            test.log.info("\tprocessing " + f)
            fd = open(f, 'r', encoding="utf8")
            content = fd.readlines()

            for line in content:
                # line = line.strip()
                line = line.strip().replace(' ', '')

                #       no commented lines            no McTest cmds
                if (not line.startswith('#')) and (not ("devboard" in line)) and (
                        (keyword1 in line) or ((keyword2 != "") and (keyword2 in line))):

                    # at cmd formats '<at>', "<at>", f'at', f"at"
                    if line.rfind("(") > -1:
                        start = line.rfind("('") + 2
                        if start > 1:
                            end = line.find("'", start)
                        else:
                            start = line.rfind("(\"") + 2
                            if start > 1:
                                end = line.find("\"", start)
                            else:
                                start = line.rfind("(f'") + 3
                                if start > 1:
                                    end = line.find("'", start)

                    if end - start > 0 and end > -1:
                        at_cmd = line[start:end]
                        # test.log.info("\t-> " + at_cmd + ", Start: " + str(start) + ", End: " + str(end))

                        if at_cmd.startswith(('AT', 'at')):
                            file = Path(f).name

                            if at_cmd in at_dict:
                                file = Path(f).name
                                tuple = at_dict[at_cmd]

                                # tuple[0]: TC/DSTL
                                # tuple[1]: list of filenames
                                if (not ftype in tuple[0]):
                                    new_type = str(tuple[0]) + ", " + str(ftype)
                                    at_dict[at_cmd] = (new_type, tuple[1])

                                if (not file in tuple[1]):
                                    new_file = str(tuple[1]) + "," + str(file)
                                    type = at_dict[at_cmd][0]
                                    at_dict[at_cmd] = (type, new_file)

                            else:
                                # add command to dictionary
                                #file = Path(f).name
                                at_dict[at_cmd] = (ftype, str(file))

                            ctr += 1

        test.log.info("Found keyword " + keyword1 + " " + str(ctr) + " times in " + ftype)

    def run(test):
        pattern = test.get('file_pattern')
        keyword1 = test.get('keyword1')
        keyword2 = test.get('keyword2')
        base_dir = test.get('base_dir')

        # read AT commands from test cases
        path = base_dir + 'tests\\device_management\\iot_service_agent'
        ftype = "TC"
        test.parse_path(test, path, keyword1, keyword2, pattern, ftype)

        # read AT commands from relevant DSTL's
        path = base_dir + 'dstl\\miscellaneous'
        ftype = "DSTL"
        test.parse_path(test, path, keyword1, keyword2, pattern, ftype)

        test.expect(len(at_dict) > 0)
        test.expect(os.path.isfile(out_file))

    def cleanup(test):
        # sort dictionary
        test.log.info("Number of AT commands found: " + str(len(at_dict)))
        test.log.info(f'{70 * "#"}')

        log_fd.write("List of AT commands generated by " + testkey + " (" + test.test_file + ")\n\n")

        for key in sorted(at_dict):
            test.log.info(key)
            log_fd.write(key + "\n")
        log_fd.write(key + "\n\n")
        test.log.info("")

        for key in sorted(at_dict):
            test.log.info(key)
            log_fd.write(key + "\n")
            test.log.info("used in: " + str(at_dict[key][0]))
            log_fd.write(" used in: " + str(at_dict[key][0]) + "\n")

            file_list = str(at_dict[key][1]).strip().split(",")

            for i in file_list:
                test.log.info("\t" + str(i))
                log_fd.write("\t" + str(i) + "\n")
            test.log.info("")
            log_fd.write("\n")

        test.log.info(f'{70 * "#"}')

        log_fd.close()

        # test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
        #                                testkey, str(test.test_result), test.campaign_file,
        #                                test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')
        pass


if "__main__" == __name__:
    unicorn.main()
