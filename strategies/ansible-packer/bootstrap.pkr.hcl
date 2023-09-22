packer {
  required_plugins {
    arm-image = {
      source  = "github.com/solo-io/arm-image"
      version = "~> 0.2.7"
    }

    ansible = {
      version = "~> 1.1.0"
      source  = "github.com/hashicorp/ansible"
    }
  }
}

variable "source_iso_url" {
  type = string
}

variable "source_iso_sha256" {
  type = string
}

source "arm-image" "pi" {
  chroot_mounts = [
    ["proc", "proc", "/proc"],
    ["sysfs", "sysfs", "/sys"],
    ["bind", "/dev", "/dev"],
    ["devpts", "devpts", "/dev/pts"],
    ["binfmt_misc", "binfmt_misc", "/proc/sys/fs/binfmt_misc"],
  ]
  image_type           = "raspberrypi"
  iso_checksum         = "${var.source_iso_sha256}"
  iso_target_extension = "img"
  iso_url              = "${var.source_iso_url}"
  output_filename      = "dmp-pi.img"
  target_image_size    = 5368709120 // 5GB, RPiOS is 4.5GB inflated
}

build {
  sources = ["source.arm-image.pi"]

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y python3 python3-pip",
      "pip3 install --upgrade pip",
      "pip3 install --upgrade setuptools wheel",
      "pip3 install ansible passlib",
      "sudo apt-get remove -y rustc cargo",
      "sudo apt-get autoremove -y",
      "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
      "sudo apt-get install -y -f"
    ]
  }

  provisioner "ansible" {
    ansible_env_vars = [
      "ANSIBLE_FORCE_COLOR=1",
      "PYTHONUNBUFFERED=1",
    ]
    extra_arguments  = [
      # The following arguments are required for running Ansible within a chroot
      # See https://www.packer.io/plugins/provisioners/ansible/ansible#chroot-communicator for details
      "--connection=chroot",
      "--become-user=root",
      "-e ansible_host=${build.MountPath}"
    ]
    playbook_file    = "./bootstrap.playbook.yml"
  }
}

