terraform/
├── versions.tf
├── providers.tf
├── variables.tf
├── terraform.tfvars
├── main.tf
├── outputs.tf
├── modules/
│ ├── vpc/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ └── outputs.tf
│ ├── s3/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ └── outputs.tf
│ ├── sqs/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ └── outputs.tf
│ ├── rds/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ └── outputs.tf
│ ├── eks/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ └── outputs.tf
│ ├── ec2/
│ │ ├── main.tf
│ │ ├── variables.tf
│ │ ├── outputs.tf
│ │ └── userdata.sh.tpl
│ └── security/
│ ├── main.tf
│ ├── variables.tf
│ └── outputs.tf
