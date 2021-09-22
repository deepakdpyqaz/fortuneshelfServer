from apscheduler.schedulers.background import BackgroundScheduler

from schedular.tester import testFunc
import pytz

class Schedular:
    timezone=pytz.timezone("Asia/Kolkata")
    def run(self):
        from schedular.language_schedular import languageSchedular
        from schedular.category_schedular import categorySchedular
        from schedular.order_cleanup import orderCleanup
        scheduler = BackgroundScheduler()
        scheduler.add_job(languageSchedular,"cron",minute="*",hour=2,day="*",month="*",day_of_week="MON-SUN",timezone=self.timezone)
        scheduler.add_job(categorySchedular,"cron",minute="*",hour=2,day="*",month="*",day_of_week="MON-SUN",timezone=self.timezone)
        scheduler.add_job(orderCleanup,"cron",minute="*",hour=2,day="*",month="*",day_of_week="MON-SUN",timezone=self.timezone)
        scheduler.start()