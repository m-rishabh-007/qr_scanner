from django.urls import path

from .views import (
    DraftSelectionView,
    FeedbackSubmitView,
    GenerateDraftsView,
    PublicEventView,
    QuestionnaireConfigView,
    SessionCreateView,
)

urlpatterns = [
    path("qr/<str:qr_token>/config/", QuestionnaireConfigView.as_view()),
    path("qr/<str:qr_token>/sessions/", SessionCreateView.as_view()),
    path("sessions/<str:session_token>/feedback/", FeedbackSubmitView.as_view()),
    path("sessions/<str:session_token>/generate/", GenerateDraftsView.as_view()),
    path("sessions/<str:session_token>/select/", DraftSelectionView.as_view()),
    path("sessions/<str:session_token>/events/", PublicEventView.as_view()),
]
