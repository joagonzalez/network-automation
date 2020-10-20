import sys
sys.path.append('../')
import requests
import pymsteams
from config.settings import config

WEBHOOK_URL = config['TEAMS']['WEBHOOK_URL']

def send_teams_message(message):

    # You must create the connectorcard object with the Microsoft Webhook URL
    myTeamsMessage = pymsteams.connectorcard(WEBHOOK_URL)

    # Add text to the message.
    myTeamsMessage.text(message)

    # send the message.
    myTeamsMessage.send()

def send_teams_card_message(title, activity_title, activity_subtitle=None, activity_image=None, activity_text=None,
                            facts=None, section_text=None, section_image=None, section_image_title=None):
    myTeamsMessage = pymsteams.connectorcard(CONFIG['TEAMS']['WEBHOOK_URL'])
    # create the section
    myMessageSection = pymsteams.cardsection()
    myMessageSection.title(title)

    # Activity Elements
    if activity_title != None:
        myMessageSection.activityTitle(activity_title)
    if activity_title != None:
        myMessageSection.activitySubtitle(activity_subtitle)
    if activity_title != None:
        myMessageSection.activityImage(activity_image)
    if activity_title != None:
        myMessageSection.activityText(activity_text)

    # Facts are key value pairs displayed in a list.
    if len(facts) != 0:
       for fact in facts:
            myMessageSection.addFact(fact['name'], fact['value'])

    # Section Text
    myMessageSection.text(section_text)

    # Section Images
    if section_image != 'False':
        myMessageSection.addImage(section_image, ititle=section_image_title)

    # Add your section to the connector card object before sending
    myTeamsMessage.addSection(myMessageSection)
    myTeamsMessage.summary("Flask-API automatic message")

    myTeamsMessage.printme()

    return myTeamsMessage.send()
    

def send_teams_test_message():
    myTeamsMessage = pymsteams.connectorcard(CONFIG['TEAMS']['WEBHOOK_URL'])
    # create the section
    myMessageSection = pymsteams.cardsection()

    # Section Title
    myMessageSection.title("Section title")

    # Activity Elements
    myMessageSection.activityTitle("my activity title")
    myMessageSection.activitySubtitle("my activity subtitle")
    myMessageSection.activityImage("http://i.imgur.com/c4jt321l.png")
    myMessageSection.activityText("This is my activity Text")

    # Facts are key value pairs displayed in a list.
    myMessageSection.addFact("this", "is fine")
    myMessageSection.addFact("this is", "also fine")

    # Section Text
    myMessageSection.text("This is my section text")

    # Section Images
    myMessageSection.addImage("http://i.imgur.com/c4jt321l.png", ititle="This Is Fine")

    # Add your section to the connector card object before sending
    myTeamsMessage.addSection(myMessageSection)
    myTeamsMessage.summary("Test Message")

    myTeamsMessage.printme()

    result = myTeamsMessage.send()
    return result

if __name__ == '__main__':
    print(send_teams_message(sys.argv[1]))