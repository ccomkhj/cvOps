import os
import boto3
import yaml
import argparse
from botocore.exceptions import NoCredentialsError


# Function to load AWS credentials
def load_aws_credentials(config_path="config/s3_credentials.yaml"):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config["aws_access_key_id"], config["aws_secret_access_key"]


# Main download function
def download_s3_files(
    aws_access_key_id, aws_secret_access_key, bucket_name, s3_prefix, local_directory
):
    try:
        # Create an S3 client with specified credentials
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        # List all objects in the specified S3 path
        objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)

        # Iterate through the objects and download each file
        for obj in objects.get("Contents", []):
            key = obj["Key"]
            local_file_path = os.path.join(
                local_directory, key[len(s3_prefix) :]
            )  # Adjust local file path

            # Create local directories if they don't exist
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            print(f"Downloading {key} to {local_file_path}")
            s3.download_file(bucket_name, key, local_file_path)

        print("Download complete.")
    except NoCredentialsError:
        print("Credentials not available.")


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
