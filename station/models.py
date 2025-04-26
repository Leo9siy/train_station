from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('first_name', 'last_name')
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='source_route')
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='destination_route')
    distance = models.IntegerField()

    class Meta:
        unique_together = ('source', 'destination')

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='route_journey')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='train_journey')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["route", "train"],
                name='unique_route_train'
            ),
        ]

    def __str__(self):
        return f"{self.train} -> {self.route}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = get_user_model()

    def __str__(self):
        return f"{self.created_at}"


class Ticket(models.Model):
    cargo = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    seat = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_tickets')

    class Meta:
        unique_together = ('cargo', 'seat')

    def __str__(self):
        return f"{self.cargo} {self.seat} {self.order}"
