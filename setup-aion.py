import requests
import json
import argparse
import time
import logging
import sys
import copy
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
        resp = s.send(prepreq, timeout=60, allow_redirects=allow_redirects, stream=stream, verify=verify)
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
    parser.add_argument("--admin_password", help="Admin Password", type=str,
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
    parser.add_argument("--local_admin_password", help="Local Admin Password", type=str,
                        default="")
    parser.add_argument("--node_storage_provider", help="Node Storage Provider", type=str,
                        default="local")
    parser.add_argument("--node_storage_remote_uri", help="Node Storage Remote URL", type=str,
                        default="")

    parser.add_argument("--deploy_location", help="Deploy location name", type=str,
                        default="location1")
    parser.add_argument("--deploy_products", help="Deploy product list \'[{\"name\":\"product-name\", \"version\":\"0.0\"}]\'", type=str,
                        default="")
    parser.add_argument("--entitlements", help="License entitlement list \'[{\"product\":\"product-name\", \"license\":\"license-name\", \"number\":100}]\'", type=str,
                        default="")

    parser.add_argument("--wait_timeout", help="Time in seconds to wait for platform initialization", type=str,
                        default=900)
    parser.add_argument("-v", "--verbose", help="Verbose logging", type=str2bool,
                        default=False)
    parser.add_argument("--log_file", help="Log file for output. stdout when not set", type=str, default="")

    args = parser.parse_args()
    if args.admin_password == "":
        raise Exception("admin password must be specified")
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


def initialize_platform(c, org_info, user_info):
    app_url = get_app_url(c)

    hdrs = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    wait_time = int(c["wait_timeout"])

    init_data = get_server_init_data(c, org_info, user_info)

    # retry 1st app_url request until timeout or success
    start_time = time.time()
    while True:
        try:
            r = request(app_url + "/api/local/initialization").json()
        except Exception as e:
            r = None

        if r:
            break

        if (time.time() - start_time) > wait_time:
            raise Exception("Failed to receive response from %s" %
                            app_url + "/api/local/initialization")
        time.sleep(5)
        LOG.debug("retrying %s" % app_url + "/api/local/initialization")

    LOG.debug("intialization: %s" % json.dumps(r))
    if r["initialized"]:
        LOG.debug("platform already initialized")
        return

    data = {
        "config": {
            "provider": "local",
            "remote_uri": ""
        }
    }
    local_storage = request(app_url + "/api/local/storage/test", headers=hdrs, data=data).json()
    LOG.debug("localStorage: %s" % json.dumps(local_storage))

    LOG.debug("ServerFormingNewCluster: %s" % json.dumps(init_data))
    r = request(app_url + "/api/local/initialization/server-forming-new-cluster",
                headers=hdrs, data=init_data)

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

    return


def install_products(app_url, app_token, new_product_list, deploy_location):
    hdrs = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + app_token,
    }
    LOG.info("install products: %s" % json.dumps(new_product_list, indent=4))

    products = request(app_url + "/api/cluster/temeva-proxy/api/inv/products",
                       headers=hdrs).json()
    LOG.debug("available products: %s" % json.dumps(products, indent=4))

    install_products = []
    for np in new_product_list:
        name = np.get("name")
        version = np.get("version")
        id = None
        for p in products:
            if p.get("name") == name:
                version_summaries = p.get("version_summaries")
                if not version_summaries:
                    continue
                for v in version_summaries:
                    if not version or v.get("version") == version:
                        install_products.append({
                            "name": p["name"],
                            "product_id": p["id"],
                            "version": v.get("version"),
                            "version_id": v.get("id")
                        })

    # get node
    nodes = request(app_url + "/api/cluster/nodes?view=identity-only",
                    headers=hdrs).json()
    if not nodes:
        LOG.error("no cluster nodes found. skip product install")
        return
    LOG.debug("nodes: %s" % json.dumps(nodes))

    for p in install_products:
        data = {
            "type": "product",
            "product": {
                "product_version_id": p["version_id"]
            }
        }
        LOG.info("sync product %s" % (p["name"]))
        sync = request(app_url + "/api/cluster/updates/x/start-sync",
                       headers=hdrs, data=data).json()
        LOG.debug("sync: %s" % json.dumps(sync))

        # wait for product sync...
        start_time = time.time()
        product_ok = False
        deployed = False
        while True:
            time.sleep(5)
            local_products = request(app_url + "/api/inv/products",
                                     headers=hdrs).json()
            for lp in local_products:
                if p["product_id"] != lp["id"]:
                    continue
                for vs in lp.get("version_summaries", []):
                    if p["version_id"] == vs["id"]:
                        product_ok = True
                        deployed = lp.get("deployed")
                        break
            if product_ok:
                break
            if (time.time() - start_time) > 60:
                break
            LOG.debug("retrying product list %s" % app_url + "/api/inv/products")

        if not product_ok:
            raise Exception("product %s sync failed." % p["name"])
        if deployed:
            LOG.info("product %s is already deployed" % p["name"])
            continue

        data = {
            "id": None,
            "product_version": {
                "artifacts": [],
                "id": p["version_id"],
                "version": None,
                "upgrade_available": False
            },
            "initial_location_name": deploy_location,
            "state": "initializing",
            "error": None
        }
        temp_hdrs = copy.deepcopy(hdrs)
        LOG.info("deploying product %s" % (p["name"]))
        LOG.debug("deploying product %s data: %s" % (p["name"], data))
        try:
            # single node
            r = request(app_url + "/api/local/product-instances",
                        headers=temp_hdrs, data=data).json()
        except Exception as e:
            LOG.debug("product-instances exception: %s" % str(e))
            # multi node
            r = request(app_url + "/api/cluster/node-proxy/" +
                        nodes[0]["id"] + "/api/local/product-instances",
                        headers=temp_hdrs, data=data).json()

        LOG.debug("deploy product response: %s" % json.dumps(r))


def entitlement_match(new_entitlement_list, e):
    if e["disabled"]:
        return -1

    details = ast.literal_eval(e["details"])
    for i, ne in enumerate(new_entitlement_list):
        if ne.get("id") == e.get("id"):
            # if the id matches don't check anything else
            return i
        product = ne.get("product")
        if product and product != details.get("application_name"):
            continue
        count = ne.get("number")
        if count and str(count) != str(details.get("max_concurrency")):
            continue
        if ne.get("license") == details.get("license_id"):
            if details["concurrent_host_limit"] <= len(e["hosted_entitlements"]):
                continue
            return i
    return -1


def install_entitlements(aion_url, access_token, app_url, app_token, platform_addr, new_entitlement_list):
    hdrs = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + app_token,
    }

    LOG.info("install entitlements: %s" % json.dumps(new_entitlement_list, indent=4))

    workspaces = request(app_url + "/api/cluster/temeva-proxy/api/iam/workspaces",
                         headers=hdrs).json()
    LOG.debug("workspaces: %s" % json.dumps(workspaces))

    entitlements = request(app_url +
                           "/api/cluster/temeva-proxy/api/lic/entitlements?" +
                           "search=&entdetail=summary&show_hardware=false",
                           headers=hdrs).json()
    LOG.debug("entitlements: %s" % json.dumps(entitlements, indent=4))

    local_entitlements = request(app_url + "/api/lic/entitlements?" +
                                 "workspace_id=all&entdetail=summary&show_hardware=false&" +
                                 "show_software=true&include_set=15",
                                 headers=hdrs).json()
    LOG.debug("local entitlements: %s" % json.dumps(local_entitlements, indent=4))

    entitlement_ids = []
    match_list = list(new_entitlement_list)
    LOG.debug("checking for match: %s" % json.dumps(match_list))

    for e in local_entitlements:
        mi = entitlement_match(match_list, e)
        if mi >= 0:
            LOG.info("entitlement already installed: %s" % json.dumps(match_list[mi]))
            del match_list[mi]
            if not match_list:
                break

    for e in entitlements:
        mi = entitlement_match(match_list, e)
        if mi >= 0:
            entitlement_ids.append(e["id"])
            del match_list[mi]
            if not match_list:
                break

    if match_list:
        LOG.warning("unable to find entitlements: %s" % json.dumps(match_list))

    if not entitlement_ids:
        return

    LOG.debug("installing entitlements %s" % ",".join(entitlement_ids))
    cluster = request(app_url + "/api/cluster/clusters/my",
                      headers=hdrs).json()
    aion_hdrs = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
        "Origin": "https://" + platform_addr,
        "Referer": "https://" + platform_addr + "/"
    }
    resp = request(aion_url + "/api/lic/entitlements/x/bulk-host",
                   headers=aion_hdrs, method="OPTIONS")

    aion_hdrs = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }
    host_id = cluster["id"]
    data = {
        "host_id": host_id,
        "entitlement_ids": entitlement_ids
    }

    bulk_host = request(aion_url + "/api/lic/entitlements/x/bulk-host",
                        headers=aion_hdrs, data=data).json()

    data = {
        "type": "entitlement"
    }
    start_sync = request(app_url + "/api/cluster/updates/x/start-sync",
                         headers=hdrs, data=data).json()


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

    initialize_platform(c, org_info, user_info)

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

    new_product_list = c.get("deploy_products")
    if new_product_list:
        # short sleep may fix issue with intermittent product sync not working w/ older AION versions
        time.sleep(15)
        new_product_list = json.loads(new_product_list)
        install_products(app_url, app_token, new_product_list, c["deploy_location"])

    new_entitlement_list = c.get('entitlements')
    if new_entitlement_list:
        new_entitlement_list = json.loads(new_entitlement_list)
        install_entitlements(aion_url, access_token, app_url, app_token, c["platform_addr"], new_entitlement_list)


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
