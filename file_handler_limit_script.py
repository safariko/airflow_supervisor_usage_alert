import json
import smtplib
from smtplib import *
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path
from sys import stderr, stdout, argv

import subprocess

# INITIALIZE VARIABLES
SYSTEM_TYPE = None

if len(argv) == 2:
    SYSTEM_TYPE = argv[1]

full_path = path.realpath(__file__)
pathname = path.dirname(full_path)


with open(pathname + '/startup_parameters.json') as json_data:
    startup = json.load(json_data)
    json_data.close()

logging_dt_format = '%d/%b/%Y %H:%M:%S'


FROM_ADDRESS = startup[SYSTEM_TYPE]['Email']['FromAddress']
FROM_PSWD = startup[SYSTEM_TYPE]['Email']['FromPSWD']
TO_ADDRESS = startup[SYSTEM_TYPE]['Email']['ToAddress']
CC_ADDRESS = startup[SYSTEM_TYPE]['Email']['CcAddress']
BCC_ADDRESS = startup[SYSTEM_TYPE]['Email']['BccAddress']

servers = startup[SYSTEM_TYPE]["Servers"]


today = datetime.now()
today.strftime('%m%d%y')
today = today.strftime('%Y%m%d')


def main():
    print('[' + datetime.now().strftime(logging_dt_format) +
          '][INFO][main] Start connecting to supervisor servers ...',
          file=stdout, flush=True)

    email_dictionary = {}

    for server in servers:
        ratio = get_ratio(server)
        save_ratio(server, ratio)
        email_dictionary[server] = ratio

    sendEmail(email_dictionary)

def get_ratio(server):
    ou = subprocess.Popen(servers[server], stdout=subprocess.PIPE, shell=True)
    output = ou.stdout.read()
    string_output = output.decode('utf-8')
    string_output_no_tabs = string_output.replace('\t', ' ')
    string_output_no_end = string_output_no_tabs.replace('\n', ' ')
    output_list = string_output_no_end.split(' ')
    active = float(output_list[0])
    limit = float(output_list[2])
    ratio = round(active/limit, 2)

    return ratio


def save_ratio(server, ratio):
    with open("file_handler_usage_stats.txt", "a") as f:
        f.write(datetime.now().strftime(logging_dt_format) + '\n')
        f.write(server + '\n')
        f.write(str(ratio) + '\n')


#  CREATE AND SEND EMAIL
def sendEmail(email_dict):
    print('[' + datetime.now().strftime(logging_dt_format) +
          '][INFO] Creating Email...', flush=True)
    send_email_dict = {}

    for server, ratio in email_dict.items():
        if float(ratio) >= 0.5:
            send_email_dict[server] = ratio

    if len(send_email_dict) == 0:
        return


    msg = MIMEMultipart()
    msg['From'] = FROM_ADDRESS
    msg['To'] = TO_ADDRESS
    msg['Cc'] = CC_ADDRESS
    msg['Bcc'] = BCC_ADDRESS
    msg['Subject'] = "Usage of file hanlders is above the threshold"

    recipient = CC_ADDRESS.split(",") + BCC_ADDRESS.split(",") + [TO_ADDRESS]

    body = "Hi Team, \n\nPlease see below the troubling server(s) and the latest usage ratio.\n\n"

    for key, value in send_email_dict.items():
        body = body + key + ":\t" + str(value) + "\n"

    body = body + "\n\nThank you.\n" +"Safar Kurbansho"+ '\n\n'

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.outlook.com', 587)
        server.starttls()
        server.login(FROM_ADDRESS, FROM_PSWD)
        text = msg.as_string()
        server.sendmail(FROM_ADDRESS, recipient, text)
        print('[' + datetime.now().strftime(logging_dt_format) +
              '][INFO] Email Sent.', flush=True)
        print('[' + datetime.now().strftime(logging_dt_format) +
              '][INFO] File Hanlder Check Complete', flush=True)
        server.quit()
    except SMTPResponseException as e:
        error_code = e.smtp_code
        error_message = e.smtp_error
        print("Error code:" + str(error_code))
        print("Message:" + str(error_message))
        if (error_code == 422):
            print("Recipient Mailbox Full")
        elif (error_code == 431):
            print("Server out of space")
        elif (error_code == 447):
            print("Timeout. Try reducing number of recipients")
        elif (error_code == 510 or error_code == 511):
            print(
                "One of the addresses in your TO, CC or BBC line doesn't exist. Check again your recipients' accounts"
                " and correct any possible misspelling.")
        elif (error_code == 512):
            print(
                "Check again all your recipients' addresses: there will likely be an error in a domain name "
                "(like mail@domain.coom instead of mail@domain.com)")
        elif (error_code == 541 or error_code == 554):
            print("Your message has been detected and labeled as spam. You must ask the recipient to whitelist you")
        elif (error_code == 550):
            print(
                "Though it can be returned also by the recipient's firewall (or when the incoming server is down), "
                "the great majority of errors 550 simply tell that the recipient email address doesn't exist. "
                "You should contact the recipient otherwise and get the right address.")
        elif (error_code == 553):
            print(
                "Check all the addresses in the TO, CC and BCC field. There should be an error or a "
                "misspelling somewhere.")
        else:
            print(
            str(error_code) + ": " + str(error_message))



if __name__ == '__main__':
    main()
