from django.contrib import admin

from station.models import Ticket, Order, Crew, TrainType, Train


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
    list_filter = ["name"]
    search_fields = ["name"]


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]
