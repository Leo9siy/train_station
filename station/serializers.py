from django.db import transaction
from rest_framework import serializers

from station.models import (
    Crew,
    TrainType,
    Train,
    Station,
    Route,
    Journey,
    Order,
    Ticket,
    validate_name,
    validate_latitude,
    validate_departure_and_arrival,
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]
        read_only_fields = ("id",)

    def validate(self, data):
        for key, value in data.items():
            validate_name(value)

        return data


class TrainTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainType
        fields = ["id", "name"]
        read_only_fields = ("id",)


class TrainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Train
        fields = [
            "id",
            "name",
            "is_big",
            "all_seats",
            "cargo_num",
            "places_in_cargo",
            "train_type",
        ]


class TrainDetailSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )


class StationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station
        fields = ["id", "name", "latitude", "longitude"]

    def validate(self, data):
        for _, value in data.items():
            validate_latitude(value)

        return data


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]
        read_only_fields = ("id",)


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(many=False)
    destination = StationSerializer(many=False)


class JourneySerializer(serializers.ModelSerializer):
    all_seats = serializers.IntegerField(
        read_only=True,
        source="train.all_seats",
    )
    seats_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = [
            "id",
            "accessed",
            "all_seats",
            "seats_available",
            "route",
            "train",
            "crews",
            "departure_time",
            "arrival_time",
        ]
        read_only_fields = ("id",)

    def validate(self, data):
        validate_departure_and_arrival(
            data["departure_time"],
            data["arrival_time"]
        )

        return data


class JourneyListSerializer(JourneySerializer):
    crews = serializers.SlugRelatedField(
        read_only=True,
        slug_field="full_name",
        many=True,
        allow_empty=False,
    )

    train = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )

    route = serializers.SerializerMethodField()

    def get_route(self, obj):
        return f"{obj.route.__str__()}"


class JourneyDetailSerializer(JourneySerializer):
    crews = CrewSerializer(many=True, read_only=True)
    route = RouteDetailSerializer(many=False, read_only=True)
    train = TrainDetailSerializer(many=False, read_only=True)


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ["cargo", "seat", "journey"]
        read_only_fields = ("id",)

    def validate(self, data):
        train = data["journey"].train
        if data["cargo"] > train.cargo_num:
            raise serializers.ValidationError("Error")
        return data

    def create(self, validated_data):
        with transaction.atomic():
            order = Order.objects.create(user=validated_data.pop("user"))
            ticket = Ticket.objects.create(order=order, **validated_data)
            return ticket


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Order
        fields = ["tickets"]
        read_only_fields = ("id",)

    def create(self, validated_data):
        with transaction.atomic():
            tickets = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)

            for ticket in tickets:
                Ticket.objects.create(order=order, **ticket)

            return order
