terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Own key, same bucket as lexi-infra-aws and the other services' infra/ —
  # each service's state is independent, so a bad apply in one can't
  # corrupt another's.
  backend "s3" {
    bucket       = "lexi-serverless-tfstate"
    key          = "lexi-rag-srl/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}

provider "aws" {
  region = var.region
}

# Reads the VPC/RDS/IAM role/SQS queue this config depends on from
# lexi-infra-aws's state — that config is applied by hand; this one is
# what CI applies on every push to this repo's main. Its blast radius is
# only lexi-rag-srl's own function and its event source mapping.
data "terraform_remote_state" "foundation" {
  backend = "s3"

  config = {
    bucket = "lexi-serverless-tfstate"
    key    = "lexi-infra-aws/terraform.tfstate"
    region = "us-east-1"
  }
}
