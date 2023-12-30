import os
import PIL.Image as Image
import json
import base64
import io
import requests
import subprocess
from Library.vertex_ai_predict_image import predict_image_object_detection_sample
from google.cloud import aiplatform
from google.oauth2 import service_account
from google.cloud import storage
from google.auth.transport.requests import Request


def image_to_base64(image_path):
    # Open the image file
    with Image.open(image_path) as image:
        # Convert the image to RGB format (if not already in this format)
        rgb_image = image.convert('RGB')
        # Save the image into a BytesIO object (in-memory file)
        buffered = io.BytesIO()
        rgb_image.save(buffered, format="JPEG")
        # Encode this image in base64
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str


def read_image(file_path):
    with open(file_path, "rb") as file:
        image_bytes = file.read()
        encoded_string = base64.b64encode(image_bytes)
    return encoded_string


def get_access_token():
    # Get the access token from gcloud
    command = "gcloud auth print-access-token"
    process = os.popen(command)
    output = process.read()
    process.close()
    print("token:", output)
    return output


# def get_access_token():
#     token = "ya29.a0AfB_byD9meOJE7ko71Do8yfJeCc2fxId-aYj3ee7-oYXmaIz2xCrEMXTvOWvGh7Mt2BhxaJ4SZ2PoF7pcciV6zRXwcR3bnm63lgeUQQTUER4sYm_fPwcYdq2smegdN9eQSbCMMwtfLU4taUsSsUj0J3fnF0Ufih_FvYBA5-GhwaCgYKAc8SARISFQHGX2Mi59f1KsapuFYZ-kitrpiubw0177"
#     return token


def predict_from_endpoint(endpoint_id, project_id, input_data_file):
    # URL for the AI Platform prediction request
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/endpoints/{endpoint_id}:predict"

    # Headers including the authorization token
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }

    # Load the input data
    with open(input_data_file, 'r') as file:
        input_data = json.load(file)

    # Post the request
    response = requests.post(url, headers=headers, json=input_data)

    return response.json()


if __name__ == "__main__":
    json_token = 'D:/00 Project/00 My Project/Cloud Account/key_gcp/sacred-mantis-409609-cd036eaaf635.json'
    project_id = 'sacred-mantis-409609'
    project_name = 'My First Project'
    location = 'us-central1'
    endpoint_id = "4782481955662856192"
    bucket_uri = 'gs://fashion_product_classifier'

    # Update GCP credential using our json token
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_token

    # Predict image
    input_image = "./Output/Image/Blazer/1 Textured jacket.png"
    result = predict_image_object_detection_sample(
        project=project_id,
        endpoint_id=endpoint_id,
        location=location,
        filename=input_image,
        confidence_threshold=0.08,
    )
    print("Result Category:", result['displayNames'][0])
    print("Result Bounding Box:", result['bboxes'][0])

    # Predict image
    input_image = "./Output/Image/Dress/17 Gaun berpayet.png"
    result = predict_image_object_detection_sample(
        project=project_id,
        endpoint_id=endpoint_id,
        location=location,
        filename=input_image,
        confidence_threshold=0.08,
    )
    print("Result Category:", result['displayNames'][0])
    print("Result Bounding Box:", result['bboxes'][0])