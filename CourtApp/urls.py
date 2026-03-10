from django.urls import path
from . views import *

urlpatterns = [
    path("court_login/", court_login, name="court_login"),
    path("court_dashboard/", court_dashboard, name="court_dashboard"),
    path("send_evidence_req/", send_evidence_req, name="send_evidence_req"),
    path("Court_Response/", Court_Response, name="Court_Response"),
    path("decrypt_court_file/<int:id>/", decrypt_court_file, name="decrypt_court_file"),
    path("court_download_file/<int:id>/",court_download_file,name="court_download_file"),
]