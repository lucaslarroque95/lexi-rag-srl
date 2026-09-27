variable "region" {
  description = "Must match lexi-infra-aws's region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Must match lexi-infra-aws's var.project"
  type        = string
  default     = "lexi-serverless"
}

variable "embedding_model" {
  type    = string
  default = "text-embedding-3-small"
}

variable "embedding_dimension" {
  type    = number
  default = 1536
}

variable "chunk_size" {
  type    = number
  default = 1000
}

variable "chunk_overlap" {
  type    = number
  default = 200
}
