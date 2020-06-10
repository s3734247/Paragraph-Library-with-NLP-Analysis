### Deployment
- if you have venv, add venv in `.dockerignore` and `.gcloudignore`
- set `GOOGLE_APPLICATION_CREDENTIALS`
- add `.env.yaml` containing cloud sql details (refer to `.env.yaml.example`)
- `gcloud builds submit --tag gcr.io/<project>/search_app`
- `gcloud run deploy searchapp --image gcr.io/<project>/search_app --platform managed --region asia-east1 --allow-unauthenticated --set-cloudsql-instances <cloud_sql_instance>`
- the above command will output the service URL

### Test Locally
- `./startlocal.sh`
- the flask app is deployed at http://localhost:7070

## API
- /ping
    * to test whether the server is up. should return "hello world"
- POST /search, request body: json, representing the query
    * returns a list of posts, including author info
    * reponse body is json