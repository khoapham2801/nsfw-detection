// Variables to use accross the project
// which can be accessed by var.project_id
variable "project_id" {
  description = "The project ID to host the cluster in"
  default     = "mle-k3-p1"
}

variable "region" {
  description = "The region the cluster in"
  default     = "asia-southeast1"
}

# variable "bucket" {
#   description = "GCS bucket for MLE course"
#   default     = "mle-course"
# }

variable "self_link" {
  description = "The self_link of the network to attach this firewall to"
  default = "global/networks/default"
}