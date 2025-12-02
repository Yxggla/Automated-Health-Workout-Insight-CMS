from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/import", views.import_csv_view, name="import_csv"),
    path("api/seed", views.seed_templates_view, name="seed_templates"),
    path("api/templates", views.list_templates_view, name="list_templates"),
    path("api/render", views.render_template_view, name="render_template"),
    path("api/summary", views.summary_view, name="summary"),
    path("api/users", views.list_users_view, name="list_users"),
]
