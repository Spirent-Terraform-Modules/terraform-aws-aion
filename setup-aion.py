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

def request(url, data=None, method=None, headers=HDRS, params={}, allow_redirects=True, files=None, stream=False, verify=True):
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

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aion_url", help="AION URL", type=str,
                        default="https://spirent.aiontest.net", required=True)
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
    parser.add_argument("--metrics_opt_out", help="Metrics Opt Out", type=bool,
                        default=False)
    parser.add_argument("--http_enabled", help="HTTP Enabled", type=bool,
                        default=False)
    parser.add_argument("--local_admin_password", help="HTTP Enabled", type=str,
                        default="")
    parser.add_argument("--node_storage_provider", help="Node Storage Provider", type=str,
                        default="local")
    parser.add_argument("--node_storage_remote_uri", help="Node Storage Remote URL", type=str,
                        default="")
    
    parser.add_argument("--wait_timeout", help="Time in seconds to wait for platform initialization", type=str,
                        default=900)
    parser.add_argument("-v", "--verbose", help="Verbose logging", type=bool, 
                        default=False)
    parser.add_argument("--log_file", help="Log file for output. stdout when not set", type=str, default="")
    
    args = parser.parse_args()    
    if args.admin_password == "":
        raise Exceoption("admin password must be specified")
    return args

def get_server_init_data(c, orgInfo, userInfo):
    # Config Auto Fill
    org = orgInfo[0]
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
        c["admin_first_name"] = userInfo["first"]

    if not c.get("admin_last_name"):
        c["admin_last_name"] = userInfo["last"]

    if not c.get("admin_email"):
        c["admin_email"] = userInfo["email"]

    if not c.get("local_admin_password"):
        c["local_admin_password"] = c["admin_password"]
        
    emailSettings = None

    # Send Initalization
    data = {
        "cluster":{
            "name": c["cluster_name"],
            "admin":{
                "first": c["admin_first_name"],
                "last": c["admin_last_name"],
                "password": c["admin_password"],
                "email": c["admin_email"],
            },
            "organization":{
                "id": c["org_id"],
                "name": c["org_name"],
                "subdomain": c["org_subdomain"],
                "domains": c["org_domains"]
            },
            "email_settings": emailSettings,
            "metrics_opt_out": c["metrics_opt_out"],
            "web_settings":{
                "http":{
                    "enabled": c["http_enabled"],
                }
            }
        },
        "node":{
            "name": c["node_name"],
            "local_admin_password": c["local_admin_password"],
            "storage":{
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
        appUrl = "http://" + c["local_addr"]
    else:       
        appUrl = "http://" + c["platform_addr"]
    orionUrl = c["aion_url"]

    
    orgInfo = request(orionUrl + "/api/iam/organizations?subdomain=spirent").json()
    LOG.debug("orgInfo: %s" % json.dumps(orgInfo))
    
    data = {
        "grant_type": "password",
        "username": c["aion_user"],
        "password": c["aion_password"],
        "scope": orgInfo[0]["id"] 
    }
    r = request(orionUrl + "/api/iam/oauth2/token", data=data).json()
    accessToken = r["access_token"]
    LOG.debug("accessToken: %s" % accessToken)
    
    hdrs = {
        "Accept": "application/json",
        "Authorization": "Bearer " + accessToken,
    }
    userInfo = request(orionUrl + "/api/iam/users/my", headers=hdrs).json()
    LOG.debug("userInfo: %s" % json.dumps(userInfo))

    hdrs = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
        
    # Local Storage
    data = {
        "config": {
            "provider":"local",
            "remote_uri":""
        }
    }
    localStorage = request(appUrl + "/api/local/storage/test", headers=hdrs, data=data).json()
    LOG.debug("localStorage: %s" % json.dumps(localStorage))

    data = get_server_init_data(c, orgInfo, userInfo)
    LOG.debug("ServerFormingNewCluster: %s" % json.dumps(data))
    r = request(appUrl + "/api/local/initialization/server-forming-new-cluster", headers=hdrs, data=data)

    completed = False
    start_time = time.time()
    wait_time = int(c["wait_timeout"])
    if wait_time:
        LOG.info("Waiting for AION platform intialization to complete...")
        while True:
            r = request(appUrl + "/api/local/initialization").json()
            LOG.debug("intialization status: %s\n" % json.dumps(r))
            if r["initialized"]:
                completed = True
                break
            if r.get("status") == "error":
                raise Exception("failed to configure platform")
                
            if (time.time() - start_time) > wait_time:
                LOG.warning("platform initalized didn't complete in %d seconds. platform wait timed out." % wait_time)
                break
            time.sleep(2)
        
    if completed:
        LOG.info("platform initalized is complete")
    else:
        LOG.info("platform intialization may still be in progress.  Manually check platform for completion.")
    LOG.info("Exiting!")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        self.log.error('%s' % str(e))
        exit(str(e))

'''
python3 setup-aion.py --aion_url "https://spirent.aiontest.net" --platform_addr "10.109.121.113" --aion_user <user> --aion_password <password> --admin_password <password>
'''