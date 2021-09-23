from apscheduler.schedulers.background import BackgroundScheduler

import pytz

class Schedular:
    timezone=pytz.timezone("Asia/Kolkata")
    def run(self):
        from schedular.language_schedular import languageSchedular
        from schedular.category_schedular import categorySchedular
        from schedular.order_cleanup import orderCleanup
        from schedular.log_cleanup import logCleanup
        from django.conf import settings
        scheduler = BackgroundScheduler()
        if not settings.DEBUG:
            scheduler.add_job(languageSchedular,"cron",minute=30,hour=2,day="*",month="*",day_of_week="MON-SUN",timezone=self.timezone)
            scheduler.add_job(categorySchedular,"cron",minute=30,hour=2,day="*",month="*",day_of_week="MON-SUN",timezone=self.timezone)
            scheduler.add_job(orderCleanup,"cron",minute=0,hour=2,day="*",month="*",day_of_week="MON-SUN",timezone=self.timezone)
            scheduler.add_job(logCleanup,"cron",minute=0,hour=1,day="*",month="*",day_of_week="SAT",timezone=self.timezone)
        scheduler.start()