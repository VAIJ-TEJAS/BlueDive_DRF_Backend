from django.db import models

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1  # Always set the primary key to 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Settings(SingletonModel):
    scuba_limit_days = models.IntegerField()
    discount_limit_days = models.IntegerField()
    balance_payment_limit_days = models.IntegerField()

    def __str__(self):
        return f"Settings: Scuba Limit Days = {self.scuba_limit_days}, " \
               f"Discount Limit Days = {self.discount_limit_days}, " \
               f"Balance Payment Limit Days = {self.balance_payment_limit_days}"
