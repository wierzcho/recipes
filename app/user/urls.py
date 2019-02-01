from django.urls import path

from user import views

app_name = "user"
urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
    path("token/", views.GenerateTokenView.as_view(), name="token"),
    path("main/", views.ManageUserView.as_view(), name="main"),
]
