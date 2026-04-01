data "aws_region" "current" {}

# ─── AMI (Amazon Linux 2023) ────────────────────────────────────────────────
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

# ─── IAM Role for Weaviate EC2 ──────────────────────────────────────────────
resource "aws_iam_role" "weaviate" {
  name = "${var.name_prefix}-weaviate-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = { Name = "${var.name_prefix}-weaviate-ec2-role" }
}

resource "aws_iam_role_policy_attachment" "weaviate_ssm" {
  role       = aws_iam_role.weaviate.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "weaviate_s3_backup" {
  name = "${var.name_prefix}-weaviate-s3-backup"
  role = aws_iam_role.weaviate.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ]
      Resource = [
        "arn:aws:s3:::${var.name_prefix}-documents",
        "arn:aws:s3:::${var.name_prefix}-documents/weaviate-backups/*"
      ]
    }]
  })
}

resource "aws_iam_instance_profile" "weaviate" {
  name = "${var.name_prefix}-weaviate-profile"
  role = aws_iam_role.weaviate.name
}

# ─── EC2 Instance (Weaviate VectorDB) ───────────────────────────────────────
resource "aws_instance" "weaviate" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  iam_instance_profile   = aws_iam_instance_profile.weaviate.name
  key_name               = var.key_name != "" ? var.key_name : null

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
    encrypted   = true
    kms_key_id  = var.kms_key_arn
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  user_data = base64encode(templatefile("${path.module}/userdata.sh.tpl", {
    weaviate_version = var.weaviate_version
    weaviate_port    = var.weaviate_port
    grpc_port        = var.weaviate_grpc_port
    data_device      = "/dev/xvdf"
    data_mount       = "/data/weaviate"
  }))

  tags = {
    Name = "${var.name_prefix}-weaviate"
    Role = "vectordb"
  }

  lifecycle {
    ignore_changes = [ami]
  }
}

# ─── Data EBS Volume (persistent Weaviate storage) ──────────────────────────
resource "aws_ebs_volume" "weaviate_data" {
  availability_zone = aws_instance.weaviate.availability_zone
  size              = var.data_volume_size
  type              = var.data_volume_type
  iops              = var.data_volume_iops
  throughput        = var.data_volume_throughput
  encrypted         = true
  kms_key_id        = var.kms_key_arn

  tags = {
    Name = "${var.name_prefix}-weaviate-data"
    Role = "vectordb-storage"
  }
}

resource "aws_volume_attachment" "weaviate_data" {
  device_name = "/dev/xvdf"
  volume_id   = aws_ebs_volume.weaviate_data.id
  instance_id = aws_instance.weaviate.id

  stop_instance_before_detaching = true
}
