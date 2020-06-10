# Install Stackdriver logging agent
curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
sudo bash install-logging-agent.sh

# Install or update needed software
apt-get update
apt-get install -yq git supervisor python python-pip
pip install --upgrade pip virtualenv

# Account to own server process
useradd -m -d /home/pythonapp pythonapp

# Fetch source code
export HOME=/root
git clone https://github.com/s3734247/NLP2.git /opt/app
#export  GOOGLE_APPLICATION_CREDENTIALS='/opt/app/gce/woven-patrol-276308-96000b631c0e.json'

# Python environment setup
virtualenv -p python3 /opt/app/gce/env
source /opt/app/gce/env/bin/activate
sudo mkdir  /opt/app/gce/socket
sudo chmod 777 /opt/app/gce/socket

sudo wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
sudo chmod +x cloud_sql_proxy
sudo ./cloud_sql_proxy -dir=/opt/app/gce/socket   -instances="woven-patrol-276308:australia-southeast1:s3734247" \ -credential_file='/opt/app/gce/socket/woven-patrol-276308-96000b631c0e.json' &



/opt/app/gce/env/bin/pip install -r /opt/app/gce/requirements.txt

# Set ownership to newly created account
sudo chown -R pythonapp:pythonapp /opt/app

# Put supervisor configuration in proper place
sudo cp /opt/app/gce/python-app.conf /etc/supervisor/conf.d/python-app.conf

# Start service via supervisorctl
sudo supervisorctl reread
sudo supervisorctl update
