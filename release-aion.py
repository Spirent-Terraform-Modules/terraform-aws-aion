import requests
import json
import argparse
import time
import logging
import sys
import ast

HDRS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

LOG = logging.getLogger("setup_aion")


def request(url, data=None, method=None, headers=HDRS, params={}, allow_redirects=True,
            files=None, stream=False, verify=False):
    if not method:
        if data:
            method = 'POST'
        else:
            method = 'GET'
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)
    with requests.Session() as s:
        req = requests.Request(method, url, headers=headers, params=params, data=data, files=files)
        prepreq = s.prepare_request(req)
        resp = s.send(prepreq, timeout=15, allow_redirects=allow_redirects, stream=stream, verify=verify)
        if not resp.ok:
            raise Exception("request error: url:%s, code:%s, data:%s" % (url, str(resp.status_code), str(resp.text)))
        return resp


def csv_list(vstr, sep=','):
    ''' Convert a string of comma separated values to floats
        @returns iterable of floats
    '''
    values = []
    for v in vstr.split(sep):
        if v:
            values.append(v)
    return values


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_app_url(c):
    if c["local_addr"]:
        return "http://" + c["local_addr"]
    else:
        return "http://" + c["platform_addr"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aion_url",
                        help="AION URL. An example URL would be https://example.spirentaion.com", type=str,
                        default="", required=True)
    parser.add_argument("--aion_user", help="AION user", type=str,
                        required=True)
    parser.add_argument("--aion_password", help="AION password", type=str,
                        required=True)
    parser.add_argument("--local_addr",
                        help="Local API IP/host.  Will use platform_addr if not specified.",
                        type=str, default="")
    parser.add_argument("--platform_addr", help="Cluster/Node IP/host", type=str,
                        required=True)
    parser.add_argument("--admin_email", help="Admin Email", type=str,
                        default="")
    parser.add_argument("--admin_password", help="Admin Password", type=str,
                        required=True)
    parser.add_argument("--local_admin_password", help="Local Admin Password", type=str,
                        default="")

    parser.add_argument("-v", "--verbose", help="Verbose logging", type=str2bool,
                        default=False)
    parser.add_argument("--log_file", help="Log file for output. stdout when not set", type=str, default="")

    args = parser.parse_args()
    if args.admin_password == "":
        raise Exception("admin password must be specified")
    return args


def uninstall_entitlements(aion_url, access_token, app_url, app_token, platform_addr):
    hdrs = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + app_token,
    }

    aion_hdrs = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    local_entitlements = request(app_url + "/api/lic/entitlements?" +
                                 "workspace_id=all&entdetail=summary&show_hardware=false&" +
                                 "show_software=true&include_set=8",
                                 headers=hdrs).json()
    LOG.debug("local entitlements: %s" % json.dumps(local_entitlements, indent=4))

    cluster = request(app_url + "/api/cluster/clusters/my",
                      headers=hdrs).json()
    host_id = cluster["id"]

    for e in local_entitlements:
        disable = request(app_url + "/api/lic/entitlements/" + e["id"] + "/disable",
                          headers=hdrs, data=e).json()
        LOG.debug("disable entitlements: %s" % json.dumps(disable))

        details = ast.literal_eval(e["details"])
        data = {
            "host_id": host_id,
            "disabled_code": disable["disabled_code"]
        }
        request(aion_url + "/api/lic/entitlements/" + details["temeva_id"] + "/unhost",
                headers=aion_hdrs, data=data)


def main():
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    LOG.addHandler(handler)

    args = parse_args()

    if args.verbose:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.INFO)

    if args.log_file:
        log_handler = logging.FileHandler(args.log_file)
        log_handler.setFormatter(formatter)
        LOG.addHandler(log_handler)

    c = args.__dict__
    LOG.debug("Config: %s" % json.dumps(c))

    aion_url = c["aion_url"]

    org_info = request(aion_url + "/api/iam/organizations/default").json()
    LOG.debug("org_info: %s" % json.dumps(org_info))

    data = {
        "grant_type": "password",
        "username": c["aion_user"],
        "password": c["aion_password"],
        "scope": org_info["id"]
    }
    r = request(aion_url + "/api/iam/oauth2/token", data=data).json()
    access_token = r["access_token"]
    LOG.debug("access_token: %s" % access_token)

    hdrs = {
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    user_info = request(aion_url + "/api/iam/users/my", headers=hdrs).json()
    LOG.debug("userInfo: %s" % json.dumps(user_info))

    if not c.get("admin_email"):
        c["admin_email"] = user_info["email"]

    if not c.get("local_admin_password"):
        c["local_admin_password"] = c["admin_password"]

    app_url = get_app_url(c)
    org_info = request(app_url + "/api/iam/organizations/default").json()
    LOG.debug("org_info: %s" % json.dumps(org_info))

    data = {
        "grant_type": "password",
        "username": c["admin_email"],
        "password": c["admin_password"],
        "scope": org_info["id"]
    }
    r = request(app_url + "/api/iam/oauth2/token", data=data).json()
    app_token = r["access_token"]

    hdrs = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + app_token,
    }
    data = {
        "url": aion_url,
        "username": c["aion_user"],
        "password": c["aion_password"]
    }
    request(app_url + "/api/cluster/settings/temeva/login", headers=hdrs, data=data)

    uninstall_entitlements(aion_url, access_token, app_url, app_token, c["platform_addr"])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        LOG.error('%s' % str(e))
        LOG.debug('Error in release-aion', exc_info=True)
        sys.exit(str(e))

'''
python3 release-aion.py --aion_url "https://spirent.spirentaion.com" --platform_addr "10.109.121.113"
--aion_user <user> --aion_password <password> --admin_password <password>
'''
