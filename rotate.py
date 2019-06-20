import jsonFile
import json
import boto3
import smtplib
from email.message import EmailMessage
from twilio.rest import Client


# Create IAM client
iam = boto3.client('iam')
secretsManager = boto3.client('secretsmanager')


data = json.loads(jsonFile.datos)


def send_email(to, accesKey):
    print("Sending email to " + to)
    msg = EmailMessage()
    msg['Subject'] = 'Automatic key Rotation'
    msg['From'] = 'acontreras@tradeprint.co.uk'
    msg['To'] = to
    msg.set_content("This is your new AWS access Key " + accesKey +
        " \n \n To retrieve your Secret, Log in to https://tradeprintdev.aws.cimpress.io/ "+
        " \n\n Go to Services/Secret Manager - look for your name on the list")

    with smtplib.SMTP('relay.fairprinthq.lan', 25) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.send_message(msg)


def grabOneKey(person):
    # List the last key used
    response = iam.list_access_keys(
        UserName=person['name'],
        # if the user has 2 keys it will select the last one created
        MaxItems=1
    )
    # grab the access key
    for i in response['AccessKeyMetadata']:
        key =(i['AccessKeyId'])
    return key


def delete_key(key, person):
    print("Deleting key " + key + " used by " + person['name'])
    iam.delete_access_key(
        UserName=person['name'],
        AccessKeyId=key
    )


def create_new_key(person):
    # create an key
    print("Creating access key for " + person['name'])
    response = iam.create_access_key(
        UserName=person['name']
    )

    # capture the json response
    r = response['AccessKey']
    return r


def update_secret_manager(person, secret):
    print("Updating the secret On Secrets Manager")
    secretsManager.update_secret(
        SecretId=person['name'],
        SecretString=secret
    )


for person in data['iam_users']:
    key = grabOneKey(person)
    delete_key(key, person)
    newKey = create_new_key(person)
    send_email(person['email'], newKey['AccessKeyId'])
    update_secret_manager(person, newKey['SecretAccessKey'])
