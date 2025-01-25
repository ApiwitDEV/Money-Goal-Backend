import main
from typing import Annotated
from fastapi import APIRouter, File, Response, UploadFile
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import storage

router = APIRouter()

@router.post('/extract-info-from-receipt')
def extract_info_from_receipt(uploaded_file: UploadFile | None = None):
    if (uploaded_file == None):
        return Response(status_code=500)
    else:
        prompt = "describe this image"
        destination_blob_name = uploaded_file.filename
        storage_client = storage.Client()
        bucket = storage_client.bucket(main.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_file(uploaded_file.file)

        model = GenerativeModel("gemini-1.5-flash-002")
        response = model.generate_content(
            [
                Part.from_uri(
                    f"gs://ex-bucket-x/{uploaded_file.filename}",
                    mime_type=uploaded_file.content_type,
                ),
                "What is shown in this image?"
            ]
        )

        blob.delete()

        return {
            "file_name": uploaded_file.filename,
            "content_type": uploaded_file.content_type,
            "file_size": uploaded_file.size,
            'detail': response.text,
            "message": "success"
        }