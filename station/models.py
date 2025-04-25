from django.core.validators import MinValueValidator
from django.db import models


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('first_name', 'last_name')
        ordering = ['first_name', 'last_name']
        index_together = ('first_name', 'last_name')

    def __str__(self):
        return f"{self.first_name} {self.last_name}


class TrainType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_name')
        ]

    def __str__(self):
        return f"{self.name}"


class Train(models.Model):
    name = models.CharField(max_length=100)
    cargo_num = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ],
    )

    places_in_cargo = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ],
    )

    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


class Station(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.name}"


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE)
    destination = models.ForeignKey(Station, on_delete=models.CASCADE)
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class Order(models.Model):


