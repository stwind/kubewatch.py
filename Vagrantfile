# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"

  config.vbguest.auto_update = false

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
  end

  config.vm.provision "shell", inline: <<-SHELL
    echo "sudo su -" >> .bashrc
  SHELL

  config.vm.provision "shell", inline: <<-SHELL
    curl -sLO https://download.docker.com/linux/ubuntu/dists/focal/pool/stable/amd64/containerd.io_1.2.13-2_amd64.deb
    curl -sLO https://download.docker.com/linux/ubuntu/dists/focal/pool/stable/amd64/docker-ce_19.03.11~3-0~ubuntu-focal_amd64.deb
    curl -sLO https://download.docker.com/linux/ubuntu/dists/focal/pool/stable/amd64/docker-ce-cli_19.03.11~3-0~ubuntu-focal_amd64.deb
    dpkg -i containerd.io_1.2.13-2_amd64.deb
    dpkg -i docker-ce-cli_19.03.11~3-0~ubuntu-focal_amd64.deb
    dpkg -i docker-ce_19.03.11~3-0~ubuntu-focal_amd64.deb
  SHELL

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update && apt-get install -y apt-transport-https curl
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
    cat << 'EOF' > /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
    apt-get update && apt-get install -y kubelet kubeadm kubectl && apt-mark hold kubelet kubeadm kubectl
  SHELL

end