from django.db import models

class Option(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=200)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='options', null=True, blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    standard_option = models.CharField(max_length=200)
    description = models.TextField()
    compulsory = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Day(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    number = models.IntegerField()

    def __str__(self):
        return str(self.number)

class EventRecord(models.Model):
    number = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_records')
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='event_records')

    def __str__(self):
        return f"EventRecord {self.number} for Event {self.event.name} on Day {self.day.number}"

class DayRecord(models.Model):
    number = models.IntegerField()
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='day_records')
    package = models.ForeignKey('Package', on_delete=models.CASCADE, related_name='day_records')

    def __str__(self):
        return f"DayRecord {self.number} for Day {self.day.number}"

class Package(models.Model):
    name = models.CharField(max_length=200)
    duration = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    pax_4_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pax_3_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pax_2_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
