import os
import streamlit as st
import io
from PIL import Image, ImageDraw
from Library.vertex_ai_predict_image import predict_image_object_detection_sample

st.set_page_config(layout="wide", page_title="Image Fashion Classifier")

st.write("## Classify the product from your image")
st.write(
    ":grin: Try uploading an image to watch the prediction and bounding box result. "
    "This code is open source and available [here](https://github.com/dmitrimahayana/Py-VertexAI-Fashion-Image-Classifier) on GitHub."
)
st.sidebar.write("## Upload and download :gear:")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
col1, col2 = st.columns(2)
my_upload = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])


def convert_img_to_bytes(input_image):
    image_original = Image.open(input_image)
    img_bytes_arr = io.BytesIO()
    image_original.save(img_bytes_arr, format=image_original.format)
    img_bytes_arr = img_bytes_arr.getvalue()
    return img_bytes_arr


def predict_image(input_image):
    json_token = 'D:/00 Project/00 My Project/Cloud Account/key_gcp/sacred-mantis-409609-cd036eaaf635.json'
    project_id = 'sacred-mantis-409609'
    project_name = 'My First Project'
    location = 'us-central1'
    endpoint_id = "4782481955662856192"
    bucket_uri = 'gs://fashion_product_classifier'

    # Define image original
    image_original = Image.open(input_image)
    image_rectangle = Image.open(input_image)
    col1.write("Original Image :camera:")
    col1.image(image_original)

    # Update GCP credential using our json token
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_token

    # Predict image
    result = predict_image_object_detection_sample(
        project=project_id,
        endpoint_id=endpoint_id,
        location=location,
        bytes_file=convert_img_to_bytes(input_image),
        confidence_threshold=0.08,
    )
    if len(result['displayNames']) > 0:
        print("Result Category:", result['displayNames'][0])
        print("Result Bounding Box:", result['bboxes'][0])
        print("Result confidences:", result['confidences'][0])
        bbox = result['bboxes'][0]
        category_name = result['displayNames'][0]

        # Get Image Size
        width, height = image_rectangle.size

        # Scale coordinates
        x_min = bbox[0] * width
        x_max = bbox[1] * width
        y_min = bbox[2] * height
        y_max = bbox[3] * height

        # Draw Rectangle
        draw = ImageDraw.Draw(image_rectangle)
        draw.rectangle([(x_min, y_min), (x_max, y_max)], outline="red", width=2)
        status = f"Prediction Image is :blue[{category_name}] :nerd_face:"
    else:
        print("no result")
        category_name = "No Result from Prediction"
        status = f":red[{category_name}] :exploding_head:"

    col2.write(status)
    col2.image(image_rectangle)


if my_upload is not None:
    if my_upload.size > MAX_FILE_SIZE:
        st.error("The uploaded file is too large. Please upload an image smaller than 5MB.")
    else:
        predict_image(my_upload)
else:
    predict_image("./Output/Image/Blazer/1 Textured jacket.png")