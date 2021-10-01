from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
import pytz
from django.conf import settings
class Schedular:
    jobstores={
        "default":RedisJobStore(settings.REDIS_DB,host=settings.REDIS_HOST,port=settings.REDIS_PORT,password=settings.REDIS_PASSWORD)
    }
    timezone=pytz.timezone("Asia/Kolkata")
    def run(self):
        from schedular.language_schedular import languageSchedular
        from schedular.category_schedular import categorySchedular
        from schedular.order_cleanup import orderCleanup
        from schedular.log_cleanup import logCleanup
        from django.conf import settings
        scheduler = BackgroundScheduler(jobstores=self.jobstores)
        if not settings.DEBUG:
            scheduler.add_job(languageSchedular,"cron",minute=30,hour=2,day="*",month="*",day_of_week="MON-SUN",timezone=self.timezone,max_instances=1,coalesce=True,id="language_schedular",replace_existing=True)
            scheduler.add_job(categorySchedular,"cron",minute=30,hour=2,day="*",month="*",day_of_week="MON-SUN",timezone=self.timezone,max_instances=1,coalesce=True,id="category_schedular",replace_existing=True)
            scheduler.add_job(orderCleanup,"cron",minute=0,hour=2,day="*",month="*",day_of_week="MON-SUN",timezone=self.timezone,max_instances=1,coalesce=True,id="order_schedular",replace_existing=True)
            scheduler.add_job(logCleanup,"cron",minute=0,hour=1,day="*",month="*",day_of_week="SAT",timezone=self.timezone,max_instances=1,coalesce=True,id="log_schedular",replace_existing=True)
        scheduler.start()