import boto3, botocore
from app import app

s3 = boto3.client (
    "s3",
    aws_access_key_id=app.config["S3_ACCESS_KEY"],
    aws_secret_access_key=app.config["S3_SECRET_KEY"]
)

def upload_file_to_s3(file, username,acl="public-read"):
    try:
        s3.upload_fileobj(
            file,
            app.config.get("S3_BUCKET"),
            "{}/{}".format(username,file.filename),
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("Error in uploading image")
        return e
    
    return "{}/{}".format(username, file.filename)
