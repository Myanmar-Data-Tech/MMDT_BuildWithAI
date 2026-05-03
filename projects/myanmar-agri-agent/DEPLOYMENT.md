# Deployment Instructions for Google Cloud Run

Follow these steps to deploy the Myanmar Farmer Assistant app to your Google Cloud Project.

## Prerequisites
1.  Ensure you have the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed.
2.  Enable the Vertex AI API in your project:
    ```bash
    gcloud services enable aiplatform.googleapis.com
    ```

## Steps

### 1. Set your Project ID
```bash
gcloud config set project dotted-cat-495205-h1
```

### 2. Build the Container Image using Cloud Build
```bash
gcloud builds submit --tag gcr.io/dotted-cat-495205-h1/myanmar-agri-agent
```

### 3. Deploy to Cloud Run
Run this command to deploy the image. ADC will be automatically used by the Cloud Run service account.
```bash
gcloud run deploy myanmar-agri-agent \
  --image gcr.io/dotted-cat-495205-h1/myanmar-agri-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 4. Access the App
Once deployed, Cloud Run will provide a Service URL (e.g., `https://myanmar-agri-agent-xyz-uc.a.run.app`). Open this in your browser to start using the app.
