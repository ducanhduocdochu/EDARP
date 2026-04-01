aws_region   = "ap-southeast-1"
project_name = "platform-rag"
environment  = "stag"

# VPC
vpc_cidr             = "10.0.0.0/16"
availability_zones   = ["ap-southeast-1a", "ap-southeast-1b"]
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]

# RDS
rds_instance_class  = "db.t3.medium"
rds_auth_db_name    = "auth_db"
rds_project_db_name = "project_db"
rds_master_username = "dbadmin"
# rds_master_password = "CHANGE_ME"  # pass via TF_VAR_rds_master_password or -var

# EKS
eks_cluster_version     = "1.29"
eks_node_instance_types = ["t3.large"]
eks_node_desired_size   = 2
eks_node_min_size       = 1
eks_node_max_size       = 4

# EC2 (Weaviate VectorDB)
weaviate_instance_type    = "r6i.xlarge"
weaviate_data_volume_size = 100
weaviate_version          = "1.28.4"
# weaviate_key_name       = "my-key-pair"  # optional, for SSH debugging

# S3
s3_force_destroy = false

# Application
# jwt_secret = "CHANGE_ME"  # pass via TF_VAR_jwt_secret or -var
llm_api_url = "http://localhost:11434"
