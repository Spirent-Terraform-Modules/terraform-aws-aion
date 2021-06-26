#!/bin/bash
python3 ${script_file}\
   --local_addr localhost\
   --platform_addr '${platform_addr}'\
   --aion_url '${aion_url}'\
   --aion_user '${aion_user}'\
   --aion_password '${aion_password}'\
   --admin_password '${admin_password}'\
   --admin_email '${admin_email}'\
   --local_admin_password '${local_admin_password}'\
   --log_file release-aion.log\
   --verbose 0
