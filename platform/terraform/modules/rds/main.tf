# ─── DB Subnet Group ─────────────────────────────────────────────────────────
resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-db-subnet"
  subnet_ids = var.private_subnet_ids

  tags = { Name = "${var.name_prefix}-db-subnet" }
}

# ─── RDS Parameter Group (PostgreSQL 16) ─────────────────────────────────────
resource "aws_db_parameter_group" "pg16" {
  name_prefix = "${var.name_prefix}-pg16-"
  family      = "postgres16"
  description = "PostgreSQL 16 parameters for ${var.name_prefix}"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name         = "shared_preload_libraries"
    value        = "pg_stat_statements"
    apply_method = "pending-reboot"
  }

  tags = { Name = "${var.name_prefix}-pg16" }
}

# ─── Auth DB (PostgreSQL for Auth Service — port 5433 internally) ────────────
resource "aws_db_instance" "auth" {
  identifier = "${var.name_prefix}-auth-db"

  engine               = "postgres"
  engine_version       = var.engine_version
  instance_class       = var.instance_class
  allocated_storage    = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_encrypted    = true
  kms_key_id           = var.kms_key_arn

  db_name  = var.auth_db_name
  username = var.master_username
  password = var.master_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.this.name
  parameter_group_name   = aws_db_parameter_group.pg16.name
  vpc_security_group_ids = [var.security_group_id]

  multi_az                = var.multi_az
  publicly_accessible     = false
  backup_retention_period = var.backup_retention_period
  skip_final_snapshot     = true
  deletion_protection     = false

  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn          = aws_iam_role.rds_monitoring.arn

  tags = { Name = "${var.name_prefix}-auth-db" }
}

# ─── Project DB (PostgreSQL for Project Service — port 5434 internally) ──────
resource "aws_db_instance" "project" {
  identifier = "${var.name_prefix}-project-db"

  engine               = "postgres"
  engine_version       = var.engine_version
  instance_class       = var.instance_class
  allocated_storage    = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_encrypted    = true
  kms_key_id           = var.kms_key_arn

  db_name  = var.project_db_name
  username = var.master_username
  password = var.master_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.this.name
  parameter_group_name   = aws_db_parameter_group.pg16.name
  vpc_security_group_ids = [var.security_group_id]

  multi_az                = var.multi_az
  publicly_accessible     = false
  backup_retention_period = var.backup_retention_period
  skip_final_snapshot     = true
  deletion_protection     = false

  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn          = aws_iam_role.rds_monitoring.arn

  tags = { Name = "${var.name_prefix}-project-db" }
}

# ─── Enhanced Monitoring IAM Role ────────────────────────────────────────────
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.name_prefix}-rds-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "monitoring.rds.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}
