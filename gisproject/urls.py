from django.urls import include, path
from rest_framework import routers

from storagis import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'importproject', views.ImportProject, basename="Import Project")

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('approvazione/', views.ApprovaBoccia.as_view()),
    path('approvazione/<str:car_id>', views.ApprovaBoccia.as_view()),
    path('bocciatura/', views.ApprovaBoccia.as_view()),
    path('bocciatura/<str:car_id>', views.ApprovaBoccia.as_view()),
    path('visualizzazione/<str:prj_id>', views.VisualizzaPrj.as_view())
]

urlpatterns += router.urls
