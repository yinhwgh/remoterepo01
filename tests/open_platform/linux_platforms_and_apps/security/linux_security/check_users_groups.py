# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw

import json

from core.basetest import BaseTest

class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
        # read the project specific user and group configuration
        try:
            json_filename = f'{test.ref_file_dir}/{test.config}.json'
            test.log.info(f"Using user and group definitions from file: {json_filename}")
        except AttributeError:
            test.fail("Missing parameter. Please provide '--ref-file-dir' and '--config'.")

        with open(json_filename) as f:
            json_data = json.load(f)
            DEFINED_USERS = json_data["users"]
            DEFINED_GROUPS = json_data["groups"]
            STRICT_USERS = json_data["strict-users"]
            STRICT_GROUPS = json_data["strict-groups"]
            MAX_UID = json_data["max-uid"]
            MAX_GID = json_data["max-gid"]
        
        test.log.info("Get list of users in the system")
        test.dut.adb.send_and_receive("cat /etc/passwd | awk -F: '{print $1\":\"$3\":\"$4}'")
        test.expect(test.dut.adb.last_retcode == 0)

        etc_passwd = parse_etc_data(test.dut.adb.last_response)
        test.log.debug(f"etc_passwd: {etc_passwd}")

        defined_users = parse_ref_data(DEFINED_USERS)
        test.log.debug(f'defined_users: {defined_users}')

        test.log.info("Check list of users in the system")
        for dut_usr, dut_uid, dut_gid in etc_passwd:
            test.log.info( f"Check if user from dut is defined: {dut_usr} dut_uid={dut_uid} dut_gid={dut_gid}" )
            test.expect(dut_usr in defined_users)
            
            if dut_usr in STRICT_USERS:
                try:
                    exp_uid, exp_gid = defined_users[dut_usr]
                    test.log.info( f"Check strict uid for user from dut: usr={dut_usr} dut_uid={dut_uid} exp_gid={exp_uid}" )
                    test.expect(dut_uid == exp_gid)
                    test.log.info( f"Check strict gid for user from dut: usr={dut_usr} dut_gid={dut_gid} exp_gid={exp_gid}" )
                    test.expect(dut_gid == exp_gid)
                except KeyError:
                    test.log.error('invalid configuration: each strict user shall be list in defined user')
            else:
                # warn if the uid or gid changed
                if dut_usr in defined_users:
                    exp_uid, exp_gid = defined_users[dut_usr]
                    if exp_uid != dut_uid:
                        test.log.warning( f"uid for user differs: usr={dut_usr} dut_uid={dut_uid} exp_uid={exp_uid}" )
                    if exp_gid != dut_gid:
                        test.log.warning( f"gid for user differs: usr={dut_usr} dut_gid={dut_gid} exp_gid={exp_gid}" )

            
        test.log.info("Check list of groups in the system")      
        test.dut.adb.send_and_receive("cat /etc/group | awk -F: '{print $1\":\"$3}'")
        test.expect(test.dut.adb.last_retcode == 0)

        etc_group = parse_etc_data(test.dut.adb.last_response)
        test.log.debug(f"etc_group: {etc_group}")

        defined_groups = parse_ref_data(DEFINED_GROUPS)
        test.log.debug(f'defined_groups: {defined_groups}')
        
        for dut_grp, dut_gid in etc_group:
            test.log.info( f"Check if group from dut is defined: {dut_grp} dut_gid={dut_gid}" )
            test.expect(dut_grp in defined_groups)

            if dut_grp in STRICT_GROUPS:
                try:
                    exp_gid = defined_groups[dut_grp][0]
                    test.log.info( f"Check strict gid for group from dut: grp={dut_grp} dut_gid={dut_gid} exp_gid={exp_gid}" )
                    test.expect(dut_gid == exp_gid)
                except KeyError:
                    test.log.error('invalid configuration: each strict group shall be list in defined groups')
            else:
                # warn if the gid changed
                if dut_usr in defined_users:
                    exp_gid = defined_groups[dut_grp][0]
                    if exp_gid != dut_gid:
                        test.log.warning( f"gid for group differs: grp={dut_grp} dut_gid={dut_gid} exp_gid={exp_gid}" )

        uids = sorted(list(map(lambda i: int(i[1]), etc_passwd)))

        # the largest uid should be nobody
        largest_uid = uids[-1]
        largest_usr = list(filter(lambda i: int(i[1]) == largest_uid, etc_passwd))[0][0]

        test.log.info(f"Check if largest uid ({largest_uid}, usr={largest_usr}) is 'nobody'")
        test.expect(largest_usr == "nobody")
        test.expect(largest_uid == 65534)

        max_uid = max(uids[0:-1])
        max_usr = list(filter(lambda i: int(i[1]) == max_uid, etc_passwd))[0][0]

        test.log.info(f"Check if max. used uid ({max_uid}, usr={max_usr}) is below {MAX_UID}")
        test.expect(max_uid < MAX_UID)

        gids = sorted(list(map(lambda i: int(i[1]), etc_group)))[0:-1]

        # the largest gid should be nogroup
        largest_gid = uids[-1]
        largest_grp = list(filter(lambda i: int(i[1]) == largest_gid, etc_group))[0][0]

        test.log.info(f"Check if largest gid ({largest_gid}, grp={largest_grp}) is 'nogroup'")
        test.expect(largest_grp == "nogroup")
        test.expect(largest_gid == 65534)

        max_gid = max(gids[0:-1])
        max_grp = list(filter(lambda i: int(i[1]) == max_gid, etc_group))[0][0]

        test.log.info(f"Check if max. used gid ({max_gid}, grp={max_grp}) is below {MAX_GID}")
        test.expect(max_gid < MAX_GID)

    def cleanup(test):
        pass

def parse_etc_data(etc_data):
        # split into lines
        data = list(etc_data.split("\n"))
        # remove '\r'
        data = list(map(lambda i: i.rstrip(), data))
        # filter empty lines
        data = list(filter(lambda i: i != '', data))
        # split at delimiter
        data = list(map(lambda i: i.split(':'), data))

        return data

def parse_ref_data(ref_data):
        data = list(map(lambda i: i.split(':'), ref_data))
        keys = list(map(lambda i: i[0], data))
        vals = list(map(lambda i: i[1:], data))
        data = dict(zip(keys, vals))

        return data

def find(line, list):
    return line in list
