from rest_framework import serializers

from station.models import Crew, TrainType, Train, Station, Route, Journey, Order, Ticket


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["first_name", "last_name"]
        read_only_fields = ('id',)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ["name"]
        read_only_fields = ('id',)


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ["name", "cargo_num", "places_in_cargo", "train_type"]


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer()


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ["name", "latitude", "longitude"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["source", "destination", "distance"]
        read_only_fields = ('id',)


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(many=False)
    destination = StationSerializer(many=False)


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ["id", "route", "train", "departure_time", "arrival_time"]
        read_only_fields = ('id',)


class JourneyDetailSerializer(JourneySerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    train = TrainSerializer(many=False, read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["cargo", "seat"]
        read_only_fields = ('id',)

    def create(self, validated_data):
        print(validated_data)
        order = Order.objects.create(user=validated_data.get("user"))
        ticket = Ticket.objects.create(order=order, **validated_data)
        return ticket


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Order
        fields = ["tickets", "user"]
        read_only_fields = ('id',)

    def create(self, validated_data):
        tickets = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)

        for ticket in tickets:
            Ticket.objects.create(order=order, **ticket)

        return order