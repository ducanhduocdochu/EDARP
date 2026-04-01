locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# ─── VPC ──────────────────────────────────────────────────────────────────────
module "vpc" {
  source = "./modules/vpc"

  name_prefix          = local.name_prefix
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

# ─── Security (IAM, Security Groups, KMS) ────────────────────────────────────
module "security" {
  source = "./modules/security"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.vpc.private_subnet_ids
}

# ─── S3 (Document Storage) ───────────────────────────────────────────────────
module "s3" {
  source = "./modules/s3"

  name_prefix   = local.name_prefix
  force_destroy = var.s3_force_destroy
  kms_key_arn   = module.security.kms_key_arn
  sqs_queue_arn = module.sqs.queue_arn
}

# ─── SQS (Async Processing Queue) ───────────────────────────────────────────
module "sqs" {
  source = "./modules/sqs"

  name_prefix = local.name_prefix
  kms_key_arn = module.security.kms_key_arn
}

# ─── RDS (PostgreSQL — auth_db, project_db) ──────────────────────────────────
module "rds" {
  source = "./modules/rds"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  security_group_id  = module.security.rds_security_group_id
  instance_class     = var.rds_instance_class
  auth_db_name       = var.rds_auth_db_name
  project_db_name    = var.rds_project_db_name
  master_username    = var.rds_master_username
  master_password    = var.rds_master_password
  kms_key_arn        = module.security.kms_key_arn
}

# ─── EC2 (Weaviate VectorDB) ─────────────────────────────────────────────────
module "ec2" {
  source = "./modules/ec2"

  name_prefix       = local.name_prefix
  vpc_id            = module.vpc.vpc_id
  subnet_id         = module.vpc.private_subnet_ids[0]
  security_group_id = module.security.weaviate_security_group_id
  instance_type     = var.weaviate_instance_type
  data_volume_size  = var.weaviate_data_volume_size
  weaviate_version  = var.weaviate_version
  kms_key_arn       = module.security.kms_key_arn
  key_name          = var.weaviate_key_name
}

# ─── EKS (Kubernetes Cluster) ────────────────────────────────────────────────
module "eks" {
  source = "./modules/eks"

  name_prefix         = local.name_prefix
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  public_subnet_ids   = module.vpc.public_subnet_ids
  cluster_version     = var.eks_cluster_version
  node_instance_types = var.eks_node_instance_types
  node_desired_size   = var.eks_node_desired_size
  node_min_size       = var.eks_node_min_size
  node_max_size       = var.eks_node_max_size
  cluster_role_arn    = module.security.eks_cluster_role_arn
  node_role_arn       = module.security.eks_node_role_arn
  security_group_id   = module.security.eks_security_group_id
}
