import os
import time
import requests
import json
from slackclient import SlackClient

BOT_ID = os.environ.get('BOT_ID')
BOT_CHANNEL = 'D4BNPGEP4'
AT_BOT = '<@{}>'.format(BOT_ID)
EXAMPLE_COMMAND = 'do'

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def parse_slack_output(output):
    if output:
        for item in output:
            try:
                print item
                if item['channel'] == BOT_CHANNEL \
                        and not item['user'] == BOT_ID \
                        and 'text' in item \
                        and not 'bot_id' in item:
                    print 'Got cmd'
                    return item['text'].strip().lower(), \
                        item['channel']
            except KeyError:
                continue
    return None, None

def parse_pr(pr_url):
    parts = pr_url.split('/')
    num = parts[-1]
    repo = parts[-3]
    org = parts[-4]
    return org, repo, num

def check_status(pr_url):
    pr = requests.get(pr_url)
    if pr.ok:
        content = json.loads(pr.text or pr.content)
        try:
            statuses_url = content['statuses_url']
            statuses = requests.get(statuses_url)
            if statuses.ok:
                content = json.loads(statuses.text or statuses.content)
                if content[0]['state'] == 'success':
                    response = 'Success!'
                else:
                    response = 'Failed.'
            else:
                response = 'Cannot get the status of the PR from github'
        except KeyError:
            response = 'Cannot find the status url in the PR page'
    else:
        response = 'Cannot get the PR page from github'

    return response

def handle_command(cmd, ch):
    response = 'Not sure what you mean. Use the {} command.'.format(EXAMPLE_COMMAND)
    if cmd.startswith(EXAMPLE_COMMAND):
        _, pr_url = cmd.split(' ')
        org, repo, num = parse_pr(pr_url)
        pr_url = 'https://api.github.com/repos/{}/{}/pulls/{}'.format(org, repo, num)
        response = check_status(pr_url)

    slack_client.api_call(
            'chat.postMessage', channel=ch, text=response, as_user=True)

if __name__ == '__main__':
    READ_WEBSOCKET_DELAY = 2
    if slack_client.rtm_connect():
        print('PRBot connected.')
        while True:
            cmd, ch = parse_slack_output(slack_client.rtm_read())
            print 'Got cmd: {}'.format(cmd)
            if cmd and ch == BOT_CHANNEL:
                print('Received cmd {} in channel {}'.format(cmd, ch))
                handle_command(cmd, ch)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection to PRBot failed')
