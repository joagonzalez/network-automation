import sys
sys.path.append('../')
from services.MSTeamsService import send_teams_message
from config.settings import config
from services.LoggerService import loggerService

if __name__ == '__main__':
    try:
        msg = sys.argv[1]
        send_teams_message(msg)
    except Exception as e:
        loggerService.error('Missing parameter or error sending message: ' + str(e))