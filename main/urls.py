from django.urls import path

from . import views

urlpatterns = [
	path('', views.home, name='home'),
    path("choose_subjects/", views.choose_subjects, name="choose_subjects"),
    path('choose_classes/', views.choose_classes, name="choose_classes"),
    path("Error/<int:code>", views.error, name="error"),
    path("Settings/", views.settings, name="settings"),
    path("Test", views.test, name="test"),
    path("FAQ/", views.FAQ_page, name="FAQ"),
    path("EULA/", views.EULA_page, name="EULA"),
    path("<slug:subject_name>/update_marks", views.update_marks, name='update marks'),
    path("<slug:slug>", views.slug_url_dispatcher, name='year page'),
    path("<slug:slug1>/<slug:slug2>", views.slug_slug_url_dispatcher, name="subject url dispatcher")
]