from django.urls import path
from . views import *

urlpatterns = [
    path("admin_login/", admin_login, name="admin_login"),
    path("admin_dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin_otp_dashboard/", admin_otp_dashboard, name="admin_otp_dashboard"),
    path("court_requests/", court_requests, name="court_requests"),
    path("admin_generate_otp/<int:id>/", admin_generate_otp, name="admin_generate_otp"),
    path("acceptrequest/<str:email>/", acceptrequest, name="acceptrequest"),
    path("rejectrequest/<str:email>/", rejectrequest, name="rejectrequest"),
    path("View_Request/", View_Request, name="View_Request"),
    path("Active_Users/", Active_Users, name="Active_Users"),
    path("Requested_Users/", Requested_Users, name="Requested_Users"),
    path("send_keys/<str:owneremail>/", send_keys, name="send_keys"),
    path('forgot-password/', forgotpass, name='forgotpass'),
    # path('reset-password/', reset_pass, name='reset_pass'),
    path('password-reset/', password_reset, name='password_reset'),
    path('update-password/', update_pass, name='update_pass'),
    path('reset-password/', reset_password, name='reset_password'),

]