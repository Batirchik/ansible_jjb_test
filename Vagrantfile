VAGRANTFILE_API_VERSION = "2"
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "geerlingguy/centos6"
  config.vm.hostname = "jenkins"
  config.vm.network :private_network, ip: "192.168.76.76"
  config.vm.network :forwarded_port, guest: 8080, host: 8080
  config.ssh.insert_key = false
  config.vm.define :jenkins
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "1024"]
  end
end