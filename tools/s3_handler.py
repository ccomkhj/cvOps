import os
import boto3
import yaml
import argparse
from botocore.exceptions import NoCredentialsError, ClientError


# Function to load AWS credentials
def load_aws_credentials(config_path="config/s3_credentials.yaml"):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config["aws_access_key_id"], config["aws_secret_access_key"]

def upload_s3_files(aws_access_key_id, aws_secret_access_key, bucket_name, local_path, s3_key):
    """
    Uploads a single file or all files within a directory to S3.
    
    Parameters:
    - aws_access_key_id: AWS access key ID.
    - aws_secret_access_key: AWS secret access key.
    - bucket_name: The name of the S3 bucket.
    - local_path: The local path to the file or directory.
    - s3_key: The S3 object key or prefix. If uploading a directory, this serves as the base path in the bucket.
    """
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    if os.path.isdir(local_path):
        # If it's a directory, upload all files within it
        for subdir, dirs, files in os.walk(local_path):
            for file in files:
                full_path = os.path.join(subdir, file)
                
                # Calculate relative path to maintain directory structure on S3
                relative_path = os.path.relpath(full_path, start=local_path).replace(os.sep, '/')
                
                # Construct full S3 path under given s3_key
                full_s3_path = f"{s3_key.rstrip('/')}/{relative_path}"
                
                try:
                    s3.upload_file(full_path, bucket_name, full_s3_path)
                    print(f"Successfully uploaded {full_path} to s3://{bucket_name}/{full_s3_path}")
                except ClientError as e:
                    print(f"Failed to upload {full_path}: {e}")
    else:
        # It's a single file
        try:
            s3_key = s3_key if s3_key else os.path.basename(local_path)
            s3.upload_file(local_path, bucket_name, s3_key)
            print(f"Successfully uploaded {local_path} to s3://{bucket_name}/{s3_key}")
        except ClientError as e:
            print(f"Failed to upload {local_path}: {e}")

# Main download function
def download_s3_files(aws_access_key_id, aws_secret_access_key, bucket_name, s3_key, local_directory):
    # Instantiate an S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    
    # Check if the s3_key denotes a single file or a directory
    if s3_key.endswith('/'):  # It's a directory
        # Make sure the local directory exists
        os.makedirs(local_directory, exist_ok=True)
        
        # List objects with the specific prefix
        objs = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_key)
        
        for obj in objs.get("Contents", []):
            key = obj["Key"]
            # Skip placeholder objects (directories in S3)
            if key.endswith('/'):
                continue
            
            relative_path = key[len(s3_key):].lstrip('/')  # Get the path relative to the s3_key
            save_path = os.path.join(local_directory, relative_path)  # Construct local path including subdirectories

            # Make sure the subdirectories exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
            print(f"Downloading {key} to {save_path}")
            s3.download_file(bucket_name, key, save_path)
            
    else:  # It's a single file
        filename = os.path.basename(s3_key)
        save_path = os.path.join(local_directory, filename)
        
        print(f"Downloading {s3_key} to {save_path}")
        s3.download_file(bucket_name, s3_key, save_path)

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Download files from AWS S3.")
    parser.add_argument("--bucket_name", help="Name of the S3 Bucket", required=False)
    parser.add_argument(
        "--s3_prefix",
        help="S3 prefix of the files to download",
        default="",
        required=False,
    )
    parser.add_argument(
        "--local_directory",
        help="Local directory to download the files",
        required=False,
    )

    args = parser.parse_args()

    # Load AWS credentials from config
    aws_access_key_id, aws_secret_access_key = load_aws_credentials()

    # Use arguments if provided, otherwise fall back to config values
    config = load_aws_credentials("config/s3_credentials.yaml")
    bucket_name = args.bucket_name if args.bucket_name else config.get("bucket_name")
    s3_prefix = args.s3_prefix
    local_directory = (
        args.local_directory if args.local_directory else config.get("local_directory")
    )

    # Ensure the local directory exists
    os.makedirs(local_directory, exist_ok=True)

    # Call the function to download files
    download_s3_files(
        aws_access_key_id,
        aws_secret_access_key,
        bucket_name,
        s3_prefix,
        local_directory,
    )


if __name__ == "__main__":
    main()
