
# Welcome to CDK V2 Python project!

![test Stacks-NG drawio](https://github.com/testinc/stacks-ng/assets/4243223/203d7e56-bd69-4c91-bb8d-8835658d7884)

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

#. Install and setup [aws-vault](https://github.com/99designs/aws-vault)
#. Your ~/.aws/config file should look something like this
```
[profile test-master]
region=us-east-1
aws_access_key_id=AKIA************
aws_secret_access_key=u4v**********************
mfa_serial=arn:aws:iam::************:mfa/<your username>

[profile test-dev]
role_arn=arn:aws:iam::806606111087:role/developer_role
mfa_serial=arn:aws:iam::************:mfa/<your username>
source_profile = test-master

[profile test-stage]
role_arn=arn:aws:iam::048857582481:role/developer_role
mfa_serial=arn:aws:iam::************:mfa/<your username>
source_profile = test-master

[profile test-prelive]
role_arn=arn:aws:iam::337635756458:role/developer_role
mfa_serial=arn:aws:iam::************:mfa/<your username>
source_profile = test-master

[profile test-prod]
role_arn=arn:aws:iam::509454863615:role/developer_role
mfa_serial=arn:aws:iam::************:mfa/<your username>
source_profile = test-master

[profile test-sandbox]
region=us-east-1
source_profile = test-master
role_arn=arn:aws:iam::655096806720:role/superuser_role
mfa_serial=arn:aws:iam::************:mfa/<your username>

```

## Switch environment by AWS Console

Use your credentials and MFA code to login test-master account, which is the landing account, then click following link to switch environment. (Only first time is needed, then you can find them in the role history)
* Develop environment: https://signin.aws.amazon.com/switchrole?roleName=developer_role&account=test-dev
* Stage environment: https://signin.aws.amazon.com/switchrole?roleName=developer_role&account=test-stage
* QA environment: https://signin.aws.amazon.com/switchrole?roleName=developer_role&account=test-prelive
* Production environment: https://signin.aws.amazon.com/switchrole?roleName=developer_role&account=test-prod
* Sandbox environment: https://signin.aws.amazon.com/switchrole?roleName=developer_role&account=test-sandbox


## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

