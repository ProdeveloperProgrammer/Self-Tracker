from django.core.management import call_command
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler import util
from django_apscheduler.models import DjangoJobExecution

def Backup():
    try:
        call_command("dbbackup",clean=True) # python manage.py dbbackup --clean
    except:
        pass

@util.close_old_connections
def delete_old_job_executions(max_age=5184000): # 2months
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(),'default')
    scheduler.add_job(Backup,trigger='interval',days=10,jobstore='default',id="backup",replace_existing=True)
    scheduler.add_job(delete_old_job_executions,trigger='interval',days=30,jobstore='default',id="delete_old_job_executions",replace_existing=True)
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()