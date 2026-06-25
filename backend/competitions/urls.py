from django.urls import path
from competitions import views

urlpatterns = [
    path("competitions/", views.list_competitions, name="competition-list"),
    path(
        "competitions/import/",
        views.import_competition,
        name="competition-import",
    ),
]
