from django.shortcuts import render
from rest_framework import viewsets

from station import serializers
from station.models import Crew, Train, TrainType, Station, Route, Journey, Order, Ticket
from station.serializers import (CrewSerializer, TrainSerializer,
                                 TrainTypeSerializer, StationSerializer, RouteSerializer, JourneySerializer,
                                 OrderSerializer, TicketSerializer, TrainDetailSerializer, RouteDetailSerializer,
                                 JourneyDetailSerializer)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TrainDetailSerializer
        return TrainSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TrainTypeSerializer
        else:
            return TrainTypeSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()


    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return self.queryset.select_related("source", "destination")

        return self.queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RouteDetailSerializer

        return RouteSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return self.queryset.select_related()
        return self.queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return JourneyDetailSerializer
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
