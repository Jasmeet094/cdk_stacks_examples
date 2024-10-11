#!/bin/bash

yum install jq -y
curl -H 'X-Key: ec663c7c0c95c8f967dcff9a4fcd32b84764c5d5e15f874f149ccedec5731a2a' 'https://cloud.tenable.com/install/agent?name=agent-name&groups=agent-group' | bash
echo "Installing ArmorPoint Agent"
aws s3api get-object --bucket finexio-devops --key armorpoint/ArmorAgent_Linux ArmorAgent_Linux
chmod 777 ArmorAgent_Linux
./ArmorAgent_Linux install 151883 bb297dbd-7a05-4b43-be6d-46451c5949d0
echo "Installing ArmorPoint EDR"
aws s3api get-object --bucket finexio-devops --key armorpoint/ArmorEDR.rpm ArmorEDR.rpm
rpm ArmorEDR.rpm -ivh
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/\(.*\)[a-z]/\1/')
SSH_DATA=$(aws secretsmanager get-secret-value --secret-id ssh-tunnel-users --query SecretString --region $REGION --output text)
User_Array+=$(echo $SSH_DATA | jq 'keys' | jq -r '.[]')

for user in $User_Array
do
ssh_key=$(echo $SSH_DATA | jq -r --arg user $user '.[$user]')
adduser $user
sudo -i -u $user bash << EOF
mkdir ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
cat > ~/.ssh/authorized_keys <<- EOM
$ssh_key
EOM
EOF
usermod $user -s /bin/false
done
cat <<EOF > /root/mysshd.te
module mysshd 1.0;

require {
    type var_log_t;
    type sshd_t;
    class file { open read write };
}

# Allow sshd to read/write to /var/log/lastlog
allow sshd_t var_log_t:file { open read write };
EOF

# Compile the policy
checkmodule -M -m -o /root/mysshd.mod /root/mysshd.te
semodule_package -o /root/mysshd.pp -m /root/mysshd.mod

# Load the policy
semodule -i /root/mysshd.pp

# Modify sshd_config to enable SSH forwarding
sed -i 's/^DisableForwarding yes/#DisableForwarding yes/' /etc/ssh/sshd_config
sed -i 's/^AllowUsers ec2-user/#AllowUsers ec2-user/' /etc/ssh/sshd_config

# Restart SSHD to apply SELinux and sshd_config changes
sudo systemctl restart sshd