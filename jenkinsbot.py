import os
import time
import sched
from slackclient import SlackClient
import jenkinsapi
from jenkinsapi.jenkins import Jenkins

jenkins = Jenkins('http://platform-jenkins.zenoss.eng')

BOT_ID = os.environ.get('BOT_ID')
BOT_CHANNEL = 'D4BNPGEP4'
AT_BOT = '<@{}>'.format(BOT_ID)

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

if __name__ == '__main__':
    core_job = jenkins.jobs['product-assembly/develop/core-pipeline']
    resmgr_job = jenkins.jobs['product-assembly/develop/resmgr-pipeline']

    def check_build(job):
        last_lgbn = 184
        lgbn = job.get_last_good_buildnumber()
        comments = []
        if not lgbn == last_lgbn:
            for changeSet in job.get_last_good_build()._data['changeSets']:
                for item in changeSet['items']:
                    username = item['author']['absoluteUrl'].split('/')[-1]
                    if username == 'ylee':
                        comments.append(item['comment'])
        if comments:
            msg = 'The following changes you made in zenoss are built in #{}\n'.format(lgbn)
            for comment in comments:
                msg += '- {}\n'.format(comment)

            notify(msg)

    def check_all_builds():
        check_build(core_job)
        check_build(resmgr_job)

    def notify(msg):
        slack_client.api_call(
               'chat.postMessage', channel=BOT_CHANNEL, text=msg, as_user=True)

    def periodic(scheduler, interval, action, actionargs=()):
        scheduler.enter(interval, 1, periodic,
                        (scheduler, interval, action, actionargs))
        action(*actionargs)

    scheduler = sched.scheduler(time.time, time.sleep)
    periodic(scheduler, 86400, check_build, (resmgr_job))
    scheduler.run()
