from rest_framework.routers import DefaultRouter

from station import views

router = DefaultRouter()
router.register("crews", views.CrewViewSet)
router.register("train-types", views.TrainTypeViewSet)
router.register("trains", views.TrainViewSet, basename="trains")
router.register("stations", views.StationViewSet)
router.register("routers", views.RouteViewSet)
router.register("journeys", views.JourneyViewSet)
router.register("orders", views.OrderViewSet)
router.register("tickets", views.TicketViewSet)


urlpatterns = router.urls

app_name = "station"
