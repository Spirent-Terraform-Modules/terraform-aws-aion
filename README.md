# AWS Spirent AION Platform Terraform

![Image of Spirent AION](./images/aion.jpg)

## Description
[Spirent AION](https://www.spirent.com/products/aion) is a cloud platform for Spirent products and license management.
This Terraform module deploys the [Spirent AION AMI](https://aws.amazon.com/marketplace/pp/prodview-xra3bq4pshjhq) on AWS using your spirentaion.com account.

After `terraform apply` finishes you will be able to point your browser at the `instance_public_ips` addresses to use the platform or perform additional configuration.

Set `enable_provisioner=false` to run the configuration wizard manually in a web browser.  Otherwise, when `enable_provisioner=false` login to https://<your_public_ip> using the values of `admin_email` and `admin_password`.

See [product configuration](#product-configuration) for automated and manual configuration details.

## Prerequisites
- AWS user credentials (environment variables AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY)
- Accept [Spirent AION AMI](https://aws.amazon.com/marketplace/pp/prodview-xra3bq4pshjhq) product subscription on AWS Marketplace
- Create an EC2 key pair on AWS for SSH access and private key file


<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| terraform | >= 0.13.0 |
| aws | >= 2.65 |

## Providers

| Name | Version |
|------|---------|
| aws | >= 2.65 |
| null | n/a |
| random | n/a |
| template | n/a |
| tls | n/a |

## Modules

No Modules.

## Resources

| Name |
|------|
| [aws_ami](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ami) |
| [aws_eip_association](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eip_association) |
| [aws_instance](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance) |
| [aws_network_interface](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/network_interface) |
| [aws_security_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) |
| [null_resource](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) |
| [random_id](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/id) |
| [template_file](https://registry.terraform.io/providers/hashicorp/template/latest/docs/data-sources/file) |
| [tls_public_key](https://registry.terraform.io/providers/hashicorp/tls/latest/docs/data-sources/public_key) |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| admin\_email | Cluster admin user email. Use this to login to instance web page.  Default is obtained from AION user information. | `string` | `""` | no |
| admin\_first\_name | Cluster admin user first name. Default is obtained from AION user information. | `string` | `""` | no |
| admin\_last\_name | Cluster admin user last name.  Default is obtained from AION user information. | `string` | `""` | no |
| admin\_password | Cluster admin user password. Use this to login to to the instance web page. | `string` | n/a | yes |
| aion\_password | AION user password for aion\_url | `string` | n/a | yes |
| aion\_url | AION URL. An example URL would be https://example.spirentaion.com. | `string` | n/a | yes |
| aion\_user | AION user registered on aion\_url | `string` | n/a | yes |
| ami | The AION AMI.  When not specified latest AMI will be used. | `string` | `""` | no |
| cluster\_names | Instance cluster names.  List length must equal instance\_count. | `list(string)` | `[]` | no |
| deploy\_location | Location name for deployed product instances. | `string` | `"location1"` | no |
| deploy\_products | List of products to deploy. See Product List below for details. | `list(map(string))` | `[]` | no |
| dest\_dir | Destination directory on the instance where provisioning files will be copied | `string` | `"~"` | no |
| eips | List of management plane elastic IP IDs.  Leave empty if subnet auto assigns IPs. | `list(string)` | `[]` | no |
| enable\_provisioner | Enable provisioning.  When enabled instances will be initialized with the specified variables. | `bool` | `true` | no |
| entitlements | Install hosted entitlements from organization's AION platform. See Entitlement List below for details. | `list(map(string))` | `[]` | no |
| http\_enabled | Allow HTTP access as well as HTTPS.  Normally this is not recommended. | `bool` | `false` | no |
| ingress\_cidr\_blocks | List of management interface ingress IPv4/IPv6 CIDR ranges.  Set to empty list when using security\_group\_ids. | `list(string)` | n/a | yes |
| instance\_count | Number of instances to create | `number` | `1` | no |
| instance\_name\_prefix | Name assigned to the AION platform instance.  An instance number will be appended to the name. | `string` | `"aion-"` | no |
| instance\_type | AWS instance type | `string` | `"m5.large"` | no |
| key\_name | AWS SSH key name to assign to each instance | `string` | n/a | yes |
| local\_admin\_password | Cluster local admin password for instance SSH access.  Will use admin\_password if not specified. | `string` | `""` | no |
| metrics\_opt\_out | Opt-out of Spirent metrics data collection | `bool` | `false` | no |
| node\_names | Instance cluster node names.  List length must equal instance\_count. | `list(string)` | `[]` | no |
| node\_storage\_provider | Cluster node storage provider | `string` | `"local"` | no |
| node\_storage\_remote\_uri | Cluster node storage URI.  Leave blank for default when provider is local | `string` | `""` | no |
| private\_key\_file | AWS key private file | `string` | n/a | yes |
| root\_block\_device | Customize details about the root block device of the instance. See Block Devices below for details. | `list(map(string))` | `[]` | no |
| security\_group\_ids | List of management plane security group IDs.  Leave empty to create a default security group using ingress\_cidr\_blocks. | `list(string)` | `[]` | no |
| subnet\_id | Management public AWS subnet ID | `string` | n/a | yes |
| vpc\_id | AWS VPC ID | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| instance\_ids | List of instance IDs |
| instance\_private\_ips | List of private IP addresses assigned to the instances, if applicable |
| instance\_public\_ips | List of public IP addresses assigned to the instances, if applicable |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->

## Block Devices

### Root Block Device
The root_block_device mapping supports the following:

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| delete_on_termination | Whether the volume should be destroyed on instance termination. | `string` | `true` | no |
| encrypted | Whether to enable volume encryption. Must be configured to perform drift detection. | `bool` | `false` | no |
| iops | Amount of provisioned IOPS. Only valid for volume_type of `io1`, `io2` or `gp3`. | `number` | n/a | no |
| kms_key_id | Amazon Resource Name (ARN) of the KMS Key to use when encrypting the volume. Must be configured to perform drift detection. | `string` | n/a | no |
| tags | A map of tags to assign to the device. | `map(string)` | `{}` | no |
| throughput | Throughput to provision for a volume in mebibytes per second (MiB/s). This is only valid for volume_type of `gp3`. | `number` | n/a | no |
| volume_size | Size of the volume in gibibytes (GiB). | `number` | n/a | no |
| volume_type | Type of volume. Valid values include `standard`, `gp2`, `gp3`, `io1`, `io2`, `sc1`, or `st1`. | `string` | `gp2` | no |


## Product Configuration
Product configuration specifies product deployment and license entitlements for the platform.

### Automated
Use Terraform variables for automated configuration.

#### Entitlement List
The entilement list specifies which license entitlements are hosted to the new AION platform.  An empty list will not add entitlements.  Use the following options to define each entitlement:

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| product | Product name | `string` | n/a | yes |
| license | License name | `string` | n/a | yes |
| number  | Entitlement number.  When specified number must match otherwise any will match.| `number` | n/a | no |

#### Product List
The product list specifies which products will be deployed.  An empty list will not deploy any products.  Use the following options to define each product deployment:

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| name | Product name | `string` | n/a | yes |
| version | Product version | `string` | n/a | yes |


### Manual
Use the web browser to perform additional manual configuration after the intance is deployed.

#### Add License Entitlements
1. From _Settings_ <img src="./images/aion_settings.jpg" width="22" height="22"/> navigate to _License Manager_, _Entitlements_
2. Click _Install Entitlements_
3. Use one of the following methods to add entitlements (#1 is prefered)
   1. Login to <your_org>.spirentaion.com and select entitlements to host in the new instance\
      **Note:** Hosted entitlements should be released before destroying the instance.  As a convenience `terraform destroy` will unhost remaining entitlements.  However, if instance state is manually manipulated you may need to contact Spirent support to release enitlements for you.
   2. Install a license entitlement file obtained from Spirent support

#### Add Products
1. From _Settings_ <img src="./images/aion_settings.jpg" width="22" height="22"/> navigate to _Settings_, _Add New Products_
2. Click _Install New Products_
3. Select products and versions and click _Install_
