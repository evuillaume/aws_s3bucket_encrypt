# S3 Auto Encrypt Bucket

*Fork of Zocdoc's Zocsec.SecurityAsCode initiative - S3-auto-encrypt*

Simplify process and add cloudformation template to create the stack.

# Set Up

Cloudformation stack need some paramters :

* **EnvironmentName**   - An environment name that will be prefixed to resource names.
* **SourceS3Bucket**   - S3 Bucket name to retrieve the Lambda source code, must be in the same region.
* **SourceS3Key** - S3 key of the ZIP file for Lambda source code. Dowload it from this repo and create a zip file in the S3 bucket.

# Deployment & Configuration

Load CloudFormation template to create all resources for the stack.

# Test It!

To test,

1. Create a new s3 bucket with no encryption.
2. Wait a few seconds.
3. Load up that s3 bucket's properties and view the updated encryption settings.
4. For optional fun, please review CloudWatch Events and CloudTrail too.

Break the rule :
1. Add Tag on the bucket : "overrideEncryption" = "true"
2. Remove encryption
3. Wait a few seconds.
4. Load up that s3 bucket's properties and view the encryption settings is always empty.

<!-- vim: spell expandtab sw=4 sts=4 ts=4
-->
