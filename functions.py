from selenium import webdriver as wb
from datetime import datetime
import time, os, requests, json
from mailjet_rest import Client


def start_chrome(headless=True):
    """
    return driver object
    """
    if not headless:
        return wb.Chrome()
    options = wb.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    chrome = wb.Chrome(options=options)
    return chrome


def log_error(error, log_file):
    """
    Logs error to a file with time stamp
    :param error: error message.
    :param log_file: file to write the log.
    :return: None
    """
    with open(os.path.join('logs', log_file), 'a') as f:
        f.write(time.ctime() + "\n" + error + "\n")


def _processes_stat(processes):
    """
    keep tracks of processes running in multiprocessing and
    hold the execution until the all the processes completes.

    :param processes: list of Process objects.
    :return: None
    """
    while True:
        ps = list(map(lambda x: x.is_alive(), processes))
        if not any(ps):
            break
        print(ps, end='\r')
        time.sleep(60)


def save_to_gcp_bucket(bucket_credentials, file_path):
    pass


def mailjet_mail(bold, message):
    api_key = os.environ['mailjet_api_key']
    api_secret = os.environ['mailjet_api_secret']
    mailjet = Client(auth=(api_key, api_secret))

    data = {
        'FromEmail': 'no-reply@robinsdeepak.tk',
        'FromName': 'Deepak Kumar',
        'Subject': 'AKU Result Alert!',

        'Text-part': 'Result Alert!',

        'Html-part': f'<h3>{bold}</h3>'
        f'<br/>{message}',

        'Recipients': [
            {
                "Email": os.environ['email1']
            },
            {
                "Email": os.environ['email2']
            }
        ]
    }
    try:
        response = mailjet.send.create(data=data)
        # print(response, "\n", response.text)
        log_error("Mail Status: \n" + json.dumps(json.loads(response.text), indent=4), "mailjet_logs.txt")
    except Exception as e:
        # print("Error!", e)
        log_error("Error sending mail: " + str(e), 'mailjet_logs.txt')
        pass


def mailjet_sms(message_data):
    token = os.environ['mailjet_sms_token']

    headers = {
        'Authorization': f'Bearer {token}',
        'content-type': 'application/json',
    }

    data = json.dumps({
        "From": "AKURES",
        "To": os.environ['phone'],
        "Text": message_data
    })

    response = requests.post('https://api.mailjet.com/v4/sms-send', headers=headers, data=data)
    with open(os.path.join('logs', 'mailJet_sent_sms.txt'), 'a') as f:
        response_data = json.loads(response.text)
        response_data['time'] = str(datetime.now())
        log_data = json.dumps(response_data, indent=4) + "\n\n\n"
        f.write(log_data)

    log_error("SMS status: " + log_data, 'mailjet_logs.txt')
