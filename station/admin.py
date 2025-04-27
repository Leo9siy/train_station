from django.contrib import admin
from django.contrib.admin import site

from station.models import Ticket, Order, Crew, TrainType, Train, Station, Route, Journey


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    model = Crew

    list_filter = ["first_name", "last_name"]
    search_fields = ["first_name", "last_name"]


@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    model = TrainType
    list_filter = ["name"]
    search_fields = ["name"]


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    model = Train
    list_filter = ["name", "train_type"]
    search_fields = ["name", "train_type__name"]
    search_help_text = "Search by name and train_type."


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    model = Station
    list_filter = ["name"]
    search_fields = ["name"]
    search_help_text = "Search by name."


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    model = Route
    list_filter = ["distance", "destination__name", "source__name"]
    search_fields = ["destination__name", "source__name"]
    search_help_text = "Search by destination and source name."


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    model = Journey
    search_fields = ["route__source__name", "route__destination__name"]
    search_help_text = "Search by source and destination name."
    list_filter = ["route__source__name", "route__destination__name"]


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    model = Ticket
    fields = ["cargo", "seat", "journey"]

    def save_model(self, request, obj, form, change):
        obj.order = Order.objects.create(user=request.user)
        super().save_model(request, obj, form, change)
