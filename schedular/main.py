from apscheduler.schedulers.background import BackgroundScheduler

from schedular.tester import testFunc
class Schedular:
    def run(self):
        from schedular.language_schedular import languageSchedular
        from schedular.category_schedular import categorySchedular
        scheduler = BackgroundScheduler()
        scheduler.add_job(languageSchedular,"interval",days=1)
        scheduler.add_job(categorySchedular,"interval",days=1)
        scheduler.start()