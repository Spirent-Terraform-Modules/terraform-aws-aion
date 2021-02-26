import requests
import json
import argparse
import time
import logging
import sys

HDRS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

LOG = logging.getLogger("setup_aion")


def request(url, data=None, method=None, headers=HDRS, params={}, allow_redirects=True,
            files=None, stream=False, verify=True):
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
            raise Exception("request error: url:%s, code:%s, data:%s" % (url, str(resp.status_code), resp.content))
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
    parser.add_argument("--platform_addr", help="Cluser/Node IP/host", type=str,
                        required=True)
    parser.add_argument("--cluster_name", help="Node Name", type=str,
                        default="")
    parser.add_argument("--node_name", help="Node Name", type=str,
                        default="")
    parser.add_argument("--admin_first_name", help="Admin First Name", type=str,
                        default="")
    parser.add_argument("--admin_last_name", help="Admin Last Name", type=str,
                        default="")
    parser.add_argument("--admin_email", help="Admin Email", type=str,
                        default="")
    parser.add_argument("--admin_password", help="Admin Email", type=str,
                        required=True)
    parser.add_argument("--org_id", help="Organization ID", type=str,
                        default="")
    parser.add_argument("--org_domains", help="Organization Domains", type=csv_list,
                        default="")
    parser.add_argument("--org_subdomain", help="Organization Subdomain", type=str,
                        default="")
    parser.add_argument("--metrics_opt_out", help="Metrics Opt Out", type=str2bool,
                        default=False)
    parser.add_argument("--http_enabled", help="HTTP Enabled", type=str2bool,
                        default=False)
    parser.add_argument("--local_admin_password", help="HTTP Enabled", type=str,
                        default="")
    parser.add_argument("--node_storage_provider", help="Node Storage Provider", type=str,
                        default="local")
    parser.add_argument("--node_storage_remote_uri", help="Node Storage Remote URL", type=str,
                        default="")

    parser.add_argument("--wait_timeout", help="Time in seconds to wait for platform initialization", type=str,
                        default=900)
    parser.add_argument("-v", "--verbose", help="Verbose logging", type=str2bool,
                        default=False)
    parser.add_argument("--log_file", help="Log file for output. stdout when not set", type=str, default="")

    args = parser.parse_args()
    if args.admin_password == "":
        raise Exceoption("admin password must be specified")
    return args


def get_server_init_data(c, org, user_info):
    # Config Auto Fill
    if not c.get("org_id"):
        c["org_id"] = org["id"]

    if not c.get("org_name"):
        c["org_name"] = org["name"]

    if not c.get("org_domains"):
        c["org_domains"] = org["domains"]

    if not c.get("org_subdomain"):
        c["org_subdomain"] = org["subdomain"]

    if not c.get("cluster_name"):
        c["cluster_name"] = c["platform_addr"]

    if not c.get("node_name"):
        c["node_name"] = c["platform_addr"]

    if not c.get("admin_firt_name"):
        c["admin_first_name"] = user_info["first"]

    if not c.get("admin_last_name"):
        c["admin_last_name"] = user_info["last"]

    if not c.get("admin_email"):
        c["admin_email"] = user_info["email"]

    if not c.get("local_admin_password"):
        c["local_admin_password"] = c["admin_password"]

    email_settings = None

    # Send Initialization
    data = {
        "cluster": {
            "name": c["cluster_name"],
            "admin": {
                "first": c["admin_first_name"],
                "last": c["admin_last_name"],
                "password": c["admin_password"],
                "email": c["admin_email"],
            },
            "organization": {
                "id": c["org_id"],
                "name": c["org_name"],
                "subdomain": c["org_subdomain"],
                "domains": c["org_domains"]
            },
            "email_settings": email_settings,
            "metrics_opt_out": c["metrics_opt_out"],
            "web_settings": {
                "http": {
                    "enabled": c["http_enabled"],
                }
            }
        },
        "node": {
            "name": c["node_name"],
            "local_admin_password": c["local_admin_password"],
            "storage": {
                "provider": c["node_storage_provider"],
                "remote_uri": c["node_storage_remote_uri"]
            }
        }
    }
    return data


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

    if c["local_addr"]:
        app_url = "http://" + c["local_addr"]
    else:
        app_url = "http://" + c["platform_addr"]
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

    hdrs = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Local Storage
    data = {
        "config": {
            "provider": "local",
            "remote_uri": ""
        }
    }

    start_time = time.time()
    wait_time = int(c["wait_timeout"])
    # retry 1st app_url request until timeout or success
    while True:
        try:
            local_storage = request(app_url + "/api/local/storage/test", headers=hdrs, data=data).json()
        except Exception as e:
            local_storage = None

        if local_storage:
            break

        if (time.time() - start_time) > wait_time:
            raise Exception("Failed to receive respone from %s" % app_url + "/api/local/storage/test")
        time.sleep(5)
        LOG.debug("retrying %s" % app_url + "/api/local/storage/test")
    LOG.debug("localStorage: %s" % json.dumps(local_storage))

    data = get_server_init_data(c, org_info, user_info)
    LOG.debug("ServerFormingNewCluster: %s" % json.dumps(data))
    r = request(app_url + "/api/local/initialization/server-forming-new-cluster", headers=hdrs, data=data)

    completed = False
    start_time = time.time()
    wait_time = int(c["wait_timeout"])
    if wait_time:
        LOG.info("Waiting for AION platform initialization to complete...")
        while True:
            try:
                r = request(app_url + "/api/local/initialization").json()
            except Exception as e:
                LOG.debug("installation status exception which may not be error: %s" % str(e))
                r = None

            if r:
                LOG.debug("initialization status: %s\n" % json.dumps(r))
                if r["initialized"]:
                    completed = True
                    break
                if r.get("status") == "error":
                    raise Exception("failed to configure platform")

            if (time.time() - start_time) > wait_time:
                LOG.warning(
                    "platform initialization didn't complete in %d seconds. platform wait timed out." % wait_time)
                break
            time.sleep(5)

    if not completed:
        raise Exception("platform initialization did not complete")

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


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        LOG.error('%s' % str(e))
        LOG.debug('Error in setup-aion', exc_info=True)
        sys.exit(str(e))

'''
python3 setup-aion.py --aion_url "https://spirent.spirentaion.com" --platform_addr "10.109.121.113"
--aion_user <user> --aion_password <password> --admin_password <password>
'''
