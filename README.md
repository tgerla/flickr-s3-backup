flickr-s3-backup
================

Back up Flickr photos on Amazon S3

Setup Virtual Env
=================

If you choose to use a [virtual environment](https://docs.python.org/3.7/tutorial/venv.html) to run your script, here is how you do it.

```bash
virtualenv -p python3 venv
```

Access the virtual env with:

```bash
source ./venv/bin/activate
```

From there you can execute the script.

Leave the virtual env with:

```bash
deactivate
```

Install Dependencies
====================

From with the virtual env, execute the following to install the dependencies:

```bash
pip3 install -r requirements.txt
```

Environment Variables
=====================

`AWS_ACCESS_KEY_ID` === The access key for your AWS account with the S3 bucket (OPTIONAL)

`AWS_SECRET_ACCESS_KEY` === The secret key for your AWS account (OPTIONAL)

`FLICKR_BUCKET` === Target AWS S3 bucket name

`FLICKR_KEY` === Flickr API key

`FLICKR_SECRET` === Flickr API secret

`FLICKR_URL` === The root Flickr URL to your photos

`S3_PATH` === The path (prefix) for the S3 keys for the photos

`S3_REGION` === AWS region where the S3 bucket resides

`S3_STORAGE_CLASS` === AWS S3 storage class (DEFAULT: `STANDARD_IA`; CHOICES: `STANDARD`|`REDUCED_REDUNDANCY`|`STANDARD_IA`|`ONEZONE_IA`|`INTELLIGENT_TIERING`|`GLACIER`|`DEEP_ARCHIVE`)

If AWS cli is installed and configured, you may not need to specify the environment variables necessary for your AWS credentials, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. See [configure credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#configuring-credentials) in boto3's documentation. There are many ways to specify your AWS credentials. Pick the one that is best for you.

