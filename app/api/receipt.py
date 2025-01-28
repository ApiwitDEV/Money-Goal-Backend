from dependencies.authentication_handler import get_user_data_from_token
import main
from typing import Annotated
from fastapi import APIRouter, Depends, File, Response, UploadFile
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import storage
import json

router = APIRouter()

prompt = '''
You are an expense report assistant.  You will receive an image of an expense receipt, and your task is to extract the total amount, any discounts, and the product list.

1. Carefully examine the provided expense receipt image: 

2. Extract the following information:
    * Total amount
    * Discount amount (if any)
    * List of products purchased, including product names, quantities, and individual prices.

3. If the image is clear and the information can be extracted, format the extracted data as a JSON object with the following structure:

```json
{
  "status": "success",
  "total": <total_amount>,
  "discount": <discount_amount>,
  "products": [
    { "name": <product_1_name>, "quantity": <product_1_quantity>, "price": <product_1_price> },
    { "name": <product_2_name>, "quantity": <product_2_quantity>, "price": <product_2_price> },
    ...
  ]
}
```

4. If the image is not clear or the information cannot be extracted, return a JSON object with the following structure:

```json
{
  "status": "failed",
  "error_message": "<A descriptive error message explaining why the extraction failed>"
}
```
'''

@router.get('/begin-resumable-upload-session/{file_name}')
def begin_resumable_upload_session(file_name: str, user: Annotated[any, Depends(get_user_data_from_token)]):
    storage_client = storage.Client()
    bucket = storage_client.bucket(main.bucket_name)
    blob = bucket.blob(file_name)
    # blob._initiate_resumable_upload()
    return blob.create_resumable_upload_session()


@router.post('/extract-info-from-receipt/{file_name}')
def extract_info_from_receipt2(file_name: str, mime_file_type: str, user: Annotated[any, Depends(get_user_data_from_token)]):
    model = GenerativeModel("gemini-1.5-flash-002")
    result = model.generate_content(
            [
                Part.from_uri(
                    f"gs://ex-bucket-x/{file_name}",
                    mime_type=mime_file_type,
                ),
                prompt
            ]
        )

    result_text = result.text
    json_string = result_text[result_text.find('{'):result_text.rfind('}') + 1]
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(main.bucket_name)
    blob = bucket.blob(file_name)
    blob.delete()

    return {
            "file_name": file_name,
            "content_type": mime_file_type,
            'detail': json.loads(json_string),
            "message": "success"
        }


@router.post('/extract-info-from-receipt')
def extract_info_from_receipt(user: Annotated[any, Depends(get_user_data_from_token)], uploaded_file: UploadFile | None = None):
    if (uploaded_file == None):
        return Response(status_code=500)
    else:
        # prompt = "describe this image"
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
                prompt
                # "What is shown in this image?"
            ]
        )

        response_text = response.text
        json_string = response_text[response_text.find('{'):response_text.rfind('}') + 1]

        blob.delete()

        return {
            "file_name": uploaded_file.filename,
            "content_type": uploaded_file.content_type,
            "file_size": uploaded_file.size,
            'detail': json.loads(json_string),
            "message": "success"
        }