from django.db.models import Count, F
from django.utils import timezone
from rest_framework import viewsets

from station.models import Crew, Train, TrainType, Station, Route, Journey, Order, Ticket
from station.serializers import (CrewSerializer, TrainSerializer,
                                 TrainTypeSerializer, StationSerializer, RouteSerializer, JourneySerializer,
                                 OrderSerializer, TicketSerializer, TrainDetailSerializer, RouteDetailSerializer,
                                 JourneyDetailSerializer, JourneyListSerializer)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TrainDetailSerializer
        return TrainSerializer

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            self.queryset = self.queryset.select_related("train_type")

        if self.action == "list":
            params = self.request.query_params.get("train_type", None)
            if params:
                ids = [int(param) for param in params.split(",")]
                self.queryset = self.queryset.filter(train_type_id__in=ids)

        return self.queryset


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_queryset(self):
        if self.action == "list":
            station_name = self.request.query_params.get("name", None)
            if station_name:
                self.queryset = self.queryset.filter(name__icontains=station_name)

        return self.queryset


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()

    def get_queryset(self):
        if self.action == "list":
            params = self.request.query_params
            if params:
                sources = params.get("source", None)
                if sources:
                    self.queryset = self.queryset.filter(source_id__in=[int(id) for id in sources.split(",")])
                destinations = params.get("destination", None)
                if destinations:
                    self.queryset = self.queryset.filter(destination_id__in=[int(id) for id in destinations.split(",")])

        if self.action in ['list', 'retrieve']:
            self.queryset = self.queryset.select_related("source", "destination")

        return self.queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RouteDetailSerializer

        return RouteSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            params = self.request.query_params
            if params:
                accessed = params.get("accessed", None)
                if accessed:
                    if accessed == 1:
                        self.queryset = self.queryset.filter(departure_time__lt=timezone.now())
                    else:
                        self.queryset = self.queryset.filter(departure_time__gt=timezone.now())

                departure_time = params.get("departure_time", None)
                if departure_time:
                    self.queryset = self.queryset.filter(departure_time__date=departure_time)

                arrival_time = params.get("arrival_time", None)
                if arrival_time:
                    self.queryset = self.queryset.filter(arrival_time__date=arrival_time)

                route = params.get("route", None)
                if route:
                    ids = [int(id) for id in route.split(",")]
                    self.queryset = self.queryset.filter(route__in=ids)

                train = params.get("train", None)
                if train:
                    ids = [int(id) for id in train.split(",")]
                    self.queryset = self.queryset.filter(train_id__in=train)

                self.queryset = self.queryset.distinct()


        if self.action in ['retrieve', "list"]:
            self.queryset = self.queryset.annotate(
                seats_available=F("train__cargo_num")
                                  * F("train__places_in_cargo")
                                  - Count("tickets")
            ).prefetch_related("tickets")

            return self.queryset.select_related(
                "route__source",
                "route__destination",
                "train__train_type",
            ).prefetch_related(
                "crews"
            )
        return self.queryset

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return JourneyDetailSerializer
        elif self.action == "list":
            return JourneyListSerializer
        return JourneySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return self.queryset.filter(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)
