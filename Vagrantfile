Vagrant.configure("2") do |config|

  config.vm.define "saraswati-debian10" do |machine|

    machine.vm.box = "generic/debian10"
    machine.vm.hostname = 'saraswati-debian10'

    machine.vm.provider :virtualbox do |v|
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 512]
      v.customize ["modifyvm", :id, "--name", "saraswati-debian10"]
    end

    machine.vm.synced_folder ".", "/src"

  end

end
