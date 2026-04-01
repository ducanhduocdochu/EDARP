variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "Project name used as prefix for resource naming"
  type        = string
  default     = "platform-rag"
}

variable "environment" {
  description = "Deployment environment (dev, stag, prod)"
  type        = string
  default     = "stag"

  validation {
    condition     = contains(["dev", "stag", "prod"], var.environment)
    error_message = "Environment must be one of: dev, stag, prod."
  }
}

# --- VPC ---
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["ap-southeast-1a", "ap-southeast-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

# --- RDS ---
variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "rds_auth_db_name" {
  description = "Database name for Auth Service"
  type        = string
  default     = "auth_db"
}

variable "rds_project_db_name" {
  description = "Database name for Project Service"
  type        = string
  default     = "project_db"
}

variable "rds_master_username" {
  description = "Master username for RDS instances"
  type        = string
  default     = "dbadmin"
}

variable "rds_master_password" {
  description = "Master password for RDS instances"
  type        = string
  sensitive   = true
}

# --- EKS ---
variable "eks_cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.29"
}

variable "eks_node_instance_types" {
  description = "EC2 instance types for EKS managed node group"
  type        = list(string)
  default     = ["t3.large"]
}

variable "eks_node_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "eks_node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "eks_node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 4
}

# --- EC2 (Weaviate VectorDB) ---
variable "weaviate_instance_type" {
  description = "EC2 instance type for Weaviate (memory-optimized recommended)"
  type        = string
  default     = "r6i.xlarge"
}

variable "weaviate_data_volume_size" {
  description = "EBS data volume size in GB for Weaviate"
  type        = number
  default     = 100
}

variable "weaviate_version" {
  description = "Weaviate Docker image version"
  type        = string
  default     = "1.28.4"
}

variable "weaviate_key_name" {
  description = "SSH key pair name for Weaviate EC2 (optional)"
  type        = string
  default     = ""
}

# --- S3 ---
variable "s3_force_destroy" {
  description = "Allow destroying S3 bucket with objects"
  type        = bool
  default     = false
}

# --- Application ---
variable "jwt_secret" {
  description = "Shared JWT secret for all services"
  type        = string
  sensitive   = true
}

variable "llm_api_url" {
  description = "LLM API endpoint (Ollama)"
  type        = string
  default     = "http://localhost:11434"
}
