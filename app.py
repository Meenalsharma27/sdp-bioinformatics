import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import boto3
from botocore.config import Config
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

# ==========================
# MySQL Configuration
# ==========================
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

mysql = MySQL(app)

# ==========================
# S3 Configuration
# ==========================
S3_BUCKET = os.getenv('S3_BUCKET')
AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')

print("S3_BUCKET =", S3_BUCKET)
print("AWS_REGION =", AWS_REGION)

if not S3_BUCKET:
    raise ValueError(
        "S3_BUCKET environment variable is missing.\n"
        "Add S3_BUCKET=<your-bucket-name> in your .env file."
    )

try:
    probe = boto3.client('s3', region_name='us-east-1')

    location = probe.get_bucket_location(
        Bucket=S3_BUCKET
    )

    AWS_REGION = (
        location.get('LocationConstraint')
        or 'us-east-1'
    )

    print("Detected bucket region:", AWS_REGION)

except Exception as e:
    print("Bucket region detection failed:", e)

s3 = boto3.client(
    's3',
    region_name=AWS_REGION,
    config=Config(
        signature_version='s3v4',
        s3={'addressing_style': 'virtual'}
    )
)

ALLOWED_IMAGE_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'webp'
}

ALLOWED_RESUME_EXTENSIONS = {
    'pdf', 'doc', 'docx'
}