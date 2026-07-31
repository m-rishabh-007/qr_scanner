from django.urls import path

from .views import FeedbackDetailView, FeedbackListView, OverviewView

urlpatterns = [
    path("overview/", OverviewView.as_view()),
    path("feedback/", FeedbackListView.as_view()),
    path("feedback/<int:feedback_id>/", FeedbackDetailView.as_view()),
]
