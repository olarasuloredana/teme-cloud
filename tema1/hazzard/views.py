from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

import oauth2client
from oauth2client import client, tools
import os
import httplib2
import base64
import logging
import requests
import datetime
import time
import http.client
from apiclient import errors, discovery
from email.mime.text import MIMEText


def index(request):
    logging.info("INDEX view entered.")
    return render(request, 'hazzard/index.html')

def get_credentials():
    SCOPES = 'https://www.googleapis.com/auth/gmail.send'
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'hazzard'

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def CreateMessage(sender, to, subject, message):
    message_text = MIMEText(message, 'html')
    message_text['to'] = to
    message_text['from'] = sender
    message_text['subject'] = subject

    raw = base64.urlsafe_b64encode(message_text.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    return body

def SendMessageInternal(service, user_id, message, to):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        logging.info('Message [Id: %s] sent to %s' % (message['id'], to))
        return message
    except errors.HttpError as error:
        logging.error('An error occurred: %s' % error)


def SendMessage(sender, to, subject, message):
    logging.info("Getting credentials...")
    credentials = get_credentials()
    logging.info("Credentials done.")

    http = credentials.authorize(httplib2.Http())
    logging.info("Credentials authorized.")

    service = discovery.build('gmail', 'v1', http=http)
    logging.info("API built.")

    message_text = CreateMessage(sender, to, subject, message)
    logging.info("Message created.")

    SendMessageInternal(service, "me", message_text, to)

def login(request):
    logging.info("LOGIN view entered.")
    to = request.POST['email']
    logging.info(to + " logged in.")
    sender = "olarasuloredana@gmail.com"
    subject = "Welcome!"
    message = "Welcome to my application!"
    SendMessage(sender, to, subject, message)
    return render(request, 'hazzard/choose.html',  {'email': to})


def earthquakes():
    now_minus_4_hours = datetime.datetime.now() - datetime.timedelta(hours=4)
    past = now_minus_4_hours.strftime("%Y-%m-%dT%H:%M:%S")

    url_earthquakes = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson'
    url_earthquakes = url_earthquakes + '&starttime=' + past

    logging.info('Earthquakes between ' + past + ' and ' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + ":")
    try:
        response = requests.get(url_earthquakes)
        json_response = response.json()
    except:
        logging.error('Error at earthquakes request!\n\n')
        return None

    if 'features' not in json_response:
        logging.error('The earthquake json does not have "features"!\n\n')
        return None

    lista = ""
    nr = 0
    for cutremur in json_response['features']:
        if 'id' not in cutremur:
            logging.warning('earthquake does not have "id"!\n\n')
            continue

        timestamp = int(cutremur['properties']['time'])
        # { 
        #     'type' : 'earthquake', 
        #     'magnitude': format(cutremur['properties']['mag'], '.2f'),
        #     'place': cutremur['properties']['place'],
        #     'time': time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(timestamp / 1000.0)),
        #     'url' : cutremur['properties']['url'],
        #     'title' : cutremur['properties']['title']
        # }
        nr += 1
        lista += str(nr) + ". <b>Title:</b> " + cutremur['properties']['title']
        lista += " <b>Place:</b> " + cutremur['properties']['place']
        lista += " <b>Time:</b> " + time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(timestamp / 1000.0))
        lista += " <b>URL:</b> " + cutremur['properties']['url'] + "<br><br>"

        logging.info(cutremur['properties']['title'] + " added to earthquake list.")

    return lista


def other_hazzards():
    url_sigimera = 'https://api.sigimera.org/v1/crises?auth_token=eHRiEPDd3HesnU9diPv4'

    try:
        response = requests.get(url_sigimera)
        json_response = response.json()
    except:
        logging.error('Error at sigimera request!\n\n')
        return None

    lista = ""
    nr = 0
    for dezastru in json_response:
        starttime = dezastru['schema_startDate'][:-1]
        # {
        #     'type' : type,
        #     'alert-level' : dezastru['crisis_alertLevel'],
        #     'country' : dezastru['gn_parentCountry'][0].title(),
        #     'time' : starttime,
        #     'url' : dezastru['rdfs_seeAlso'],
        #     'title' : dezastru['dc_title'],
        #     'description' : dezastru['dc_description']
        # }

        nr += 1
        lista += str(nr) + ". <b>Title:</b> " + dezastru['dc_title']
        lista += " <b>Alert-level:</b> " + dezastru['crisis_alertLevel']
        lista += " <b>Time:</b> " + starttime
        lista += " <b>Description:</b> " + dezastru['dc_description']
        lista += " <b>URL:</b> " + dezastru['rdfs_seeAlso'] + "<br><br>"

        logging.info(dezastru['dc_title'] + " added to hazzards list.")

    return lista


def choose(request):
    logging.info("CHOOSE view entered.")
    sender = "olarasuloredana@gmail.com"
    to = request.POST["email"]

    if 'earthquakes' in request.POST:
        logging.info("earthquakes selected.")
        subject = "Earthquakes from the last 4 hours!"
        message = earthquakes()
        if message != None:
            logging.info("earthquakes list obtained successfuly.")
            SendMessage(sender, to, subject, message)
            return render(request, 'hazzard/done.html', {"email": to})
        else:
            logging.error("Error at obtaining earthquakes list !")
            return render(request, 'hazzard/error.html', {"email": to})
    else:
        logging.info("other_hazzards selected.")
        subject = "The last 10 hazzards around the world!"
        message = other_hazzards()
        if message != None:
            logging.info("other_hazzards list obtained successfuly.")
            SendMessage(sender, to, subject, message)
            return render(request, 'hazzard/done.html', {"email": to})
        else:
            logging.error("Error at obtaining other_hazzards list !")
            return render(request, 'hazzard/error.html', {"email": to})


def back(request):
    logging.info("BACK view entered.")
    return render(request, 'hazzard/choose.html',  {'email': request.POST["email"]})

logging.basicConfig(filename='hazzard.log', level=logging.DEBUG)
