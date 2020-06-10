

Before starting:

Check your IAM with appropriate authority for SQL, storage, Compute Engine ,google Task and google NLP.
Downloading your service account file (.json)  to  /gce/socket and modify startup-script.sh  -credential_file=<path>


1. Creat queue
' gcloud tasks queues create <QUEUE_NAME>   '

And UPDATE MYSQL Table.


2. creat Compute Engine Instance:
**** startup-script.sh  is the shell file to initialize Compute Engine Instance.

  % MY_INSTANCE_NAME="my-app-instance"
  % ZONE=australia-southeast1-b
  % gcloud compute instances create $MY_INSTANCE_NAME \
    --image-family=debian-9 \
    --image-project=debian-cloud \
    --machine-type=g1-small \
    --scopes userinfo-email,cloud-platform \
    --metadata-from-file startup-script=startup-script.sh \
    --zone $ZONE \
    --tags http-server

 3. Modify Firewall (Optional)

 gcloud compute firewall-rules create de1fault-allow-http-8080 \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --description "Allow port 8080 access to http-server"



4.  Modify your "store_paragraph" cloud function， replace http target with your Compute Engine Instance IP


5.  Add Mysql connection whitelist with with your Compute Engine Instance IP


Be careful: When you Restart the instance,pleace check instance IP and command:

% supervisorctl reload
