#cloud-config
users:
  - default
  - name: debian
    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
    ssh_authorized_keys:
      - "${ssh_auth_key}"

