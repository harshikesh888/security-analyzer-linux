import os

def get_cron_jobs():

    cron = []

    folders = [
        "/etc/cron.d",
        "/etc/cron.daily",
        "/etc/cron.hourly"
    ]

    for folder in folders:
        try:
            cron.extend(
                os.listdir(folder)
            )
        except:
            pass

    return cron
