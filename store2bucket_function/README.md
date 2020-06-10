### Deployment
- set project id and google credentials
- `export upstream_topic=<trigger_topic_name>`
    * should be the same as the downstream_topic in ../xml_parser_function/.env.yaml
- create .env.yaml (refer to .env.yaml.example)
- `gcloud functions deploy store_bucket --env-vars-file .env.yaml --runtime python37 --trigger-topic $upstream_topic`