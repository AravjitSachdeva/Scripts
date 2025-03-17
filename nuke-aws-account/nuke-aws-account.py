import boto3
import yaml
import subprocess
import os

def delete_all_s3_buckets():
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
    
    # List all buckets
    response = s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    
    print(f"Found {len(buckets)} buckets to delete")
    
    # Empty and delete each bucket
    for bucket_name in buckets:
        try:
            print(f"Emptying bucket: {bucket_name}")
            bucket = s3_resource.Bucket(bucket_name)
            
            # Delete all objects (including versioned objects)
            bucket.object_versions.all().delete()
            bucket.objects.all().delete()
            
            # Delete the bucket
            print(f"Deleting bucket: {bucket_name}")
            bucket.delete()
            
            print(f"Successfully deleted bucket: {bucket_name}")
        except Exception as e:
            print(f"Error deleting bucket {bucket_name}: {str(e)}")

def create_config_file():
    config = {
        "regions": ["us-east-1", "us-east-2", "us-west-2", "global", "us-west-1"],
        "account-blocklist": ["000000000000"],
        "accounts": {
            "111111111111": {
                "filters": {
                    "IAMSAMLProvider": [
                        {"type": "glob", "value": "AWSSSO_*"}
                    ],
                    "IAMRole": [
                        {"type": "glob", "value": "AWSReservedSSO_*"}
                    ],
                    "IAMRolePolicy": [
                        {"type": "glob", "value": "AWSReservedSSO_*"}
                    ],
                    "IAMPolicy": [
                        {"type": "glob", "value": "*SSO*"}
                    ],
                    "EC2Instance": ["i-0551709afbf963571"],
                    "EC2KeyPair": ["temp-ec2"],
                    "EC2SecurityGroup": ["sg-064eb4ff256237336"]
                },
                "resource-types": {
                    "excludes": [
                        "FMSNotificationChannel", "MachineLearningEvaluation",
                        "MachineLearningBranchPrediction", "OpsWorksInstance",
                        "OpsWorksLayer", "MachineLearningDataSource",
                        "OpsWorksCMServer", "OpsWorksCMBackup",
                        "RoboMakerRobotApplication", "RoboMakerSimulationJob",
                        "Cloud9Environment", "FMSPolicy",
                        "ElasticTranscoderPreset", "RoboMakerSimulationApplication",
                        "OpsWorksCMServerState", "CloudSearchDomain",
                        "MachineLearningMLModel", "OpsWorksApp",
                        "ElasticTranscoderPipeline", "OpsWorksUserProfile",
                        "CodeStarProject", "ServiceCatalog",
                        "ServiceCatalogTagOption", "ServiceCatalogTagOptionPortfolioAttachment",
                        "S3Bucket", "S3Object", "S3MultipartUpload",
                        "S3BucketPolicy", "S3BucketPublicAccessBlock",
                        "S3BucketAnalyticsConfiguration", "S3BucketInventoryConfiguration",
                        "S3BucketMetricsConfiguration", "S3BucketEncryption",
                        "S3BucketLifecycle", "S3BucketCors",
                        "S3BucketNotification", "S3BucketReplication",
                        "S3BucketTagging", "S3BucketLogging",
                        "S3BucketWebsite", "S3BucketVersioning",
                        "S3BucketAccelerateConfiguration", "S3BucketRequestPayment",
                        "S3AccessPoint", "S3StorageLens", "S3StorageLensConfiguration"
                    ]
                }
            }
        }
    }
    
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    print("Created config.yaml file")

def run_aws_nuke():
    try:
        print("Running aws-nuke...")
        result = subprocess.run(
            ["aws-nuke", "run", "--no-dry-run", "--no-alias-check", "--log-level", "debug"],
            check=True,
            text=True,
            capture_output=True
        )
        print("aws-nuke command output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running aws-nuke: {e}")
        print("Command output:")
        print(e.stdout)
        print("Command error:")
        print(e.stderr)
    except FileNotFoundError:
        print("Error: aws-nuke command not found. Make sure aws-nuke is installed and in your PATH.")

def main():
    # Step 1: Delete all S3 buckets
    delete_all_s3_buckets()
    
    # Step 2: Create the config.yaml file for aws-nuke
    create_config_file()
    
    # Step 3: Run aws-nuke
    run_aws_nuke()

if __name__ == "__main__":
    main()
