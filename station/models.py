from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


def validate_name(name: str):
    if not name.isalpha() or not name.capitalize():
        raise ValidationError(f"Argument must be alphanumeric and capitalized, not {name}")


def validate_latitude(latitude: float):
    if not (-90 <= latitude <= 90):
        raise ValidationError(f"Argument must be between -90 and 90, not {latitude}")


def validate_departure_and_arrival(departure, arrival):
    if departure > arrival:
        raise ValidationError("Arrival must be earlier than departure")


class Crew(models.Model):
    first_name = models.CharField(max_length=255, validators=[validate_name])
    last_name = models.CharField(max_length=255, validators=[validate_name])


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        unique_together = ('first_name', 'last_name')
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True, validators=[validate_name])

    def __str__(self):
        return f"{self.name}"


class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cargo_num = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(500)
        ],
    )

    places_in_cargo = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(500)
        ],
    )

    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE, related_name='trains')

    @property
    def is_big(self):
        return self.cargo_num * self.places_in_cargo > 250

    @property
    def all_seats(self):
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return f"{self.name}"


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(
        validators=[
            validate_latitude
        ]
    )
    longitude = models.FloatField(
        validators=[
            validate_latitude
        ]
    )

    class Meta:
        unique_together = ('latitude', 'longitude')

    def __str__(self):
        return f"{self.name}"


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='source_route')
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='destination_route')
    distance = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )

    class Meta:
        unique_together = ('source', 'destination')

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class Journey(models.Model):
    crews = models.ManyToManyField(Crew, related_name='journeys')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='route_journey')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='train_journey')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    @property
    def accessed(self):
        return self.departure_time < timezone.now()

    # @property
    # def available_tickets(self):
    #     return self.train.all_seats - self.tickets.count()

    class Meta:
        unique_together = ('route', 'train')
        ordering = ["-departure_time"]


    def clean(self):
        validate_departure_and_arrival(self.departure_time, self.arrival_time)

    def __str__(self):
        return f"Train: {self.train} -> Route: {self.route} -> Accessed: {self.accessed}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

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

    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name='tickets')

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')

    class Meta:
        unique_together = ('cargo', 'seat', "journey")

    def clean(self):
        if not self.journey.accessed:
            raise ValidationError("Journey is not accessible")

        train = self.journey.train
        if self.cargo > train.cargo_num:
            raise ValidationError(f"Cargo must be less than {train.cargo_num}")
        if self.seat > train.places_in_cargo:
            raise ValidationError(f"Seat must be less than {train.places_in_cargo}")

    def __str__(self):
        return f"{self.cargo} {self.seat} {self.journey}"
