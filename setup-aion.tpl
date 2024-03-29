#!/bin/bash
python3 ${script_file}\
   --local_addr localhost\
   --platform_addr '${platform_addr}'\
   --aion_url '${aion_url}'\
   --aion_user '${aion_user}'\
   --aion_password '${aion_password}'\
   --cluster_name '${cluster_name}'\
   --node_name '${node_name}'\
   --admin_password '${admin_password}'\
   --admin_first_name '${admin_first_name}'\
   --admin_last_name '${admin_last_name}'\
   --admin_email '${admin_email}'\
   --local_admin_password '${local_admin_password}'\
   --node_storage_provider '${node_storage_provider}'\
   --node_storage_remote_uri '${node_storage_remote_uri}'\
   --metrics_opt_out '${metrics_opt_out}'\
   --http_enabled '${http_enabled}'\
   --deploy_products '${deploy_products}'\
   --deploy_location '${deploy_location}'\
   --entitlements '${entitlements}'\
   --log_file setup-aion.log\
   --verbose 0
