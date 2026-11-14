from django.urls import path
from . import views


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("home/",views.home,name="home"),
    path("",views.login_page,name="login"),
    path("logout/",views.logout_page,name="logout"),
     path("regis/",views.regis,name="regis"),
    path("create/",views.create,name="create"),
    path("reiting/",views.reiting,name="reiting"),
    path("simulyator/",views.simulyator,name="simulyator"),
    path("edit/<int:id>",views.edit,name="edit"),
    path("delete/<int:id>",views.delete,name="delete"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)