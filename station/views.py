from django.db.models import Count, F, Q
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from station.models import (
    Crew,
    Train,
    TrainType,
    Station,
    Route,
    Journey,
    Order,
    Ticket,
)
from station.serializers import (
    CrewSerializer,
    TrainSerializer,
    TrainTypeSerializer,
    StationSerializer,
    RouteSerializer,
    JourneySerializer,
    OrderSerializer,
    TicketSerializer,
    TrainDetailSerializer,
    RouteDetailSerializer,
    JourneyDetailSerializer,
    JourneyListSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_queryset(self):
        if self.action == 'list':
            for field in ["first_name", "last_name"]:
                param = self.request.query_params.get(field, None)
                if param:
                    str_filter = {f"{field}__icontains": param}
                    self.queryset = self.queryset.filter(**str_filter)
        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="first_name",
                type=OpenApiTypes.STR,
                description="First name",
            ),
            OpenApiParameter(
                name="last_name",
                type=OpenApiTypes.STR,
                description="Last name",
            )
        ],
        description="Filter Crews by First Name and Last Name",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)



class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

    def get_queryset(self):
        if self.action == 'list':
            params = self.request.query_params.get("name", None)
            if params:
                self.queryset = self.queryset.filter(name__icontains=params)
        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                description="Filter by name",
            ),
        ],
        description="Filter Train Type by Name",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TrainDetailSerializer
        return TrainSerializer

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            self.queryset = self.queryset.select_related("train_type")

        if self.action == "list":
            params = self.request.query_params.get("train_type", None)
            if params:
                ids = [int(param) for param in params.split(",")]
                self.queryset = self.queryset.filter(train_type_id__in=ids)

        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "train_type",
                type={
                    "type": "array",
                    "items": {"type": "number"},
                },
                description="Filter by train_type id (ex. ?train_type=2,3)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        ### User it for filter Trains by Type ###
        return super().list(request, *args, **kwargs)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_queryset(self):
        if self.action == "list":
            station_name = self.request.query_params.get("name", None)
            if station_name:
                self.queryset = self.queryset.filter(
                    name__icontains=station_name
                )

        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type={
                    "type": "string",
                },
                description="Filter by name",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()

    def get_queryset(self):
        if self.action == "list":
            for field in ["source", "destination"]:
                params = self.request.query_params.get(field, None)
                if params:
                    self.queryset = self.queryset.filter(
                        **({f"{field}_id__in": [int(id) for id in params.split(",")]})
                    )

        if self.action in ["list", "retrieve"]:
            self.queryset = self.queryset.select_related(
                "source", "destination"
            )

        return self.queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RouteDetailSerializer

        return RouteSerializer


    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={
                    "type": "array",
                    "items": {"type": "number"},
                },
                description="Filter by source id",
            ),
            OpenApiParameter(
                "destination",
                type={
                    "type": "array",
                    "items": {"type": "number"},
                },
                description="Filter by destination id",
            ),
        ],
        description="Filter by source id (ex. ?source=2,3) and destination id (ex. ?destination=2,3)",
    )
    def list(self, request, *args, **kwargs):
        super().list(request, *args, **kwargs)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()

    def get_queryset(self):
        if self.action == "list":
            params = self.request.query_params
            if params:
                accessed = params.get("accessed", None)
                if accessed:
                    if accessed == 1:
                        self.queryset = self.queryset.filter(
                            departure_time__lt=timezone.now()
                        )
                    else:
                        self.queryset = self.queryset.filter(
                            departure_time__gt=timezone.now()
                        )

                departure_time = params.get("departure_time", None)
                if departure_time:
                    self.queryset = self.queryset.filter(
                        departure_time__date=departure_time
                    )

                arrival_time = params.get("arrival_time", None)
                if arrival_time:
                    self.queryset = self.queryset.filter(
                        arrival_time__date=arrival_time
                    )

                route = params.get("route", None)
                if route:
                    ids = [int(id) for id in route.split(",")]
                    self.queryset = self.queryset.filter(route__in=ids)

                train = params.get("train", None)
                if train:
                    ids = [int(id) for id in train.split(",")]
                    self.queryset = self.queryset.filter(train_id__in=ids)

                self.queryset = self.queryset.distinct()

        if self.action in ["retrieve", "list"]:
            self.queryset = self.queryset.annotate(
                seats_available=F("train__cargo_num")
                                * F("train__places_in_cargo")
                                - Count("tickets")
            ).prefetch_related("tickets")

            return self.queryset.select_related(
                "route__source",
                "route__destination",
                "train__train_type",
            ).prefetch_related("crews")
        return self.queryset

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
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
        if self.action in ["list", "retrieve"]:
            return self.queryset.filter(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)
