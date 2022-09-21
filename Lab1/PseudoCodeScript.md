# Pseudo Code Script
This script describes the steps we need to perform to fulfill the lab objectives.

## Create & Setup EC2 Instances

### Create Security Group for Instances
- Name: 'lab1-security-group-instances'
- [...]
- Port range: 80
- Source: 0.0.0.0/0, ::/0 (changer later to load balancer IP so that they are not accessible from the internet)

### Create VMs
- All run Ubuntu Server 64Bit
- 10 total: 5 M4.large & 5 T2.xlarge
- Give Flask installation script (bash-script)
- Security Group: select 'lab1-security-group'

### Deploy Flask Script
- HTTP on port 80



