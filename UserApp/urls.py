from django.urls import path
from . views import *

urlpatterns = [
    path("", index, name="index"),
    path("user_Registration/", user_Registration, name="user_Registration"),
    path("user_login/", user_login, name="user_login"),
    path("user_home/", user_home, name="user_home"),
    path("Upload_Files/", Upload_Files, name="Upload_Files"),
    path("View_Encrypted/", View_Encrypted, name="View_Encrypted"),
    path("view_encrypted_data/<uuid:fileid>/", view_encrypted_data, name="view_encrypted_data"),
    path("View_Response/", View_Response, name="View_Response"),
    path("decrypt_file/", decrypt_file, name="decrypt_file"),
    path("Court_Request/", Court_Request, name="Court_Request"),
    path("Share_Keys/<int:id>/", Share_Keys, name="Share_Keys"),
    path("otp/", otp, name="otp"),
    path("download_decrypt_file/<int:id>/", download_decrypt_file, name="download_decrypt_file"),
    path('check_evidence/',check_evidence,name='check_evidence')

    


]