#!/bin/bash

# Ensure all installations are done as root
sudo apt-get update -y
sudo apt-get upgrade -y

# Install .NET SDK 8.0
sudo apt-get install -y wget apt-transport-https
wget https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y dotnet-sdk-8.0

# Verify the installed version
dotnet --version

# Install awscli
sudo apt install awscli -y

# Install ruby and wget
sudo apt-get install ruby wget -y

# Install CodeDeploy Agent
cd /home/ubuntu
wget https://aws-codedeploy-us-east-1.s3.amazonaws.com/latest/install
sudo chmod +x ./install
sudo ./install auto
sudo service codedeploy-agent start
sudo service codedeploy-agent status

# Install ArmorPoint Agent
echo "Installing ArmorPoint Agent"
aws s3api get-object --bucket finexio-devops --key armorpoint/ArmorAgent_Linux ArmorAgent_Linux
chmod 777 ArmorAgent_Linux
./ArmorAgent_Linux install 151883 bb297dbd-7a05-4b43-be6d-46451c5949d0

# Install ArmorPoint EDR
echo "Installing ArmorPoint EDR"

aws s3api get-object --bucket finexio-devops --key armorpoint/ArmorEDR.rpm ArmorEDR.rpm

# Install alien + Convert the .rpm package to a .deb package and install it
sudo apt install alien -y
sudo alien -i ArmorEDR.rpm

# Install acl
sudo apt-get install -y acl

# Install jq
sudo apt-get install -y jq

# Create a group called developers
sudo groupadd developers

# Create a shared dir
sudo mkdir -p /usr/bin/fx-ng-console-app

# Assign read and execute permissions to the developers group for the shared directory
sudo setfacl -R -m g:developers:rx /usr/bin/fx-ng-console-app

# Ensure ACL permissions are set correctly on every boot
echo "@reboot root setfacl -R -m g:developers:rx /usr/bin/fx-ng-console-app" | sudo tee -a /etc/crontab

# Add Users
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/\(.*\)[a-z]/\1/')
SSH_DATA=$(aws secretsmanager get-secret-value --secret-id dotnet-console-app-users --query SecretString --region $REGION --output text)
User_Array+=$(echo $SSH_DATA | jq 'keys' | jq -r '.[]')

AllowUsersList="AllowUsers ubuntu"
for user in $User_Array
do
ssh_key=$(echo $SSH_DATA | jq -r --arg user $user '.[$user]')
adduser $user
usermod -aG developers $user
sudo -i -u $user bash << EOF
mkdir ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
cat > ~/.ssh/authorized_keys <<- EOM
$ssh_key
EOM
EOF
usermod $user -s /bin/bash
AllowUsersList+=" $user"
done

# Define the AWS region using the instance's metadata service
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/\(.*\)[a-z]/\1/')

# Install Datadog agent
DD_API_KEY=$(aws secretsmanager get-secret-value --secret-id datadog_api_key \
--query SecretString --region $REGION --output text | awk -F '"' '{print $4}')

DD_SITE="datadoghq.com"
DD_APM_INSTRUMENTATION_ENABLED="host"

# Export the variables to /etc/environment
echo "DD_API_KEY=\"$DD_API_KEY\"" | sudo tee -a /etc/environment
echo "DD_SITE=\"$DD_SITE\"" | sudo tee -a /etc/environment
echo "DD_APM_INSTRUMENTATION_ENABLED=\"$DD_APM_INSTRUMENTATION_ENABLED\"" | sudo tee -a /etc/environment

# Install Datadog agent
DD_API_KEY=$DD_API_KEY DD_SITE=$DD_SITE DD_APM_INSTRUMENTATION_ENABLED=$DD_APM_INSTRUMENTATION_ENABLED bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"


# Configure Datadog settings in datadog.yaml
echo "Configuring Datadog settings..."
sudo tee -a /etc/datadog-agent/datadog.yaml <<EOF
logs_enabled: true
tags:
  - account_env:$ENVIRONMENT
  - aws_account:$(aws sts get-caller-identity --query Account --output text)
  - instance_name:fx-ng-dotnet-console-app
EOF

# Setup custom log directory and configuration for SSH logs
echo "Setting up custom log directory for SSH logs..."
sudo mkdir -p /etc/datadog-agent/conf.d/custom_ssh_logs.d/
sudo tee /etc/datadog-agent/conf.d/custom_ssh_logs.d/conf.yaml <<EOF
logs:
  - type: file
    path: "/var/log/auth.log"
    service: "ssh_logs"
    source: "ssh"
EOF

# Change ownership of the new directory
sudo chown -R dd-agent:dd-agent /etc/datadog-agent/conf.d/custom_ssh_logs.d/

# Update permissions and restart the Datadog agent
echo "Updating permissions and restarting Datadog agent..."
sudo usermod -a -G adm dd-agent
sudo systemctl restart datadog-agent

echo "Datadog agent setup completed successfully."

# SSH configuration changes
SSHD_CONFIG="/etc/ssh/sshd_config"

# Remove any existing AllowUsers line
sed -i '/^AllowUsers/d' $SSHD_CONFIG

# Add a new AllowUsers line with the dynamically fetched users
echo "$AllowUsersList" >> $SSHD_CONFIG

# Restart the SSH service to apply changes
service sshd restart