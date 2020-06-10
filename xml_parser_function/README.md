### Deployment
- set project id and google credentials
- `export upstream_bucket=<trigger_bucket_name>`
- create .env.yaml (refer to .env.yaml.example)
- `gcloud functions deploy parse_xml --env-vars-file .env.yaml --runtime python37 --trigger-resource $upstream_bucket --trigger-event google.storage.object.finalize`