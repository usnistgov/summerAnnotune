from django.urls import path
from django.conf.urls.static import static
from . import views



urlpatterns = [ 
    path("", views.login, name="login"),
    path("homepage/<int:user_id>/", views.homepage, name="homepage"),
    path('logout/', views.logout_view, name='logout'),
    path('documents/', views.list_documents, name='documents'),
    path("codebook/<int:user_id>/", views.codebook, name="codebook"),
    path("label/<int:document_id>", views.label, name="label"),
    path('submit-data/<int:document_id>/<str:labels>/<str:pageTime>/<str:manualStatus>/', views.submit_data),
    path("fetch_data/<int:user_id>/<str:document_id>/", views.fetch_data, name="fetch_data"),
    path("skip_document/", views.skip_document),
    path('get_all_documents/', views.get_all_documents, name='get-all-documents'),
    path('labeled/<int:user_id>/', views.labeled, name='labeled'),
    path("relabel/<int:document_id>/", views.relabel, name="relabel"),
    path("documents/", views.list_documents, name="documents"),
    path("append_time/<str:pageName>/", views.append_time, name="append"),
    path('download-json/', views.download_json, name='download_json'),
    path('dashboard', views.dashboard, name="dashboard"),
    path('dashboard_data', views.dashboard_data, name="dashboard_data")
] 
