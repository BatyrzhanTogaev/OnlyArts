from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import ArtworkListView, ArtworkCreateView, ArtworkDetailView
from django.conf import settings
from django.conf.urls.static import static
from .consumers import ArtworkConsumer  # Импортируйте ваш потребитель


urlpatterns = [
    path('', ArtworkListView.as_view(), name='home'),  # Главная страница
    path('artwork/new/', ArtworkCreateView.as_view(), name='artwork-create'),
    
    # Используем ArtworkDetailView вместо функции artwork_detail
    path('ws/artwork/<int:artwork_id>/', ArtworkConsumer.as_asgi(), name='artwork-detail'),  # Используйте as_asgi() для WebSocket

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
