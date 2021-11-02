from django.urls import path
from .views import (PhotoUser, AlbumsUser, BookmarksUser, SignUpUser, SignInUser, CommentsUser,UserMe, UserId,
                    UserIdPhotos, UserIdAlbums, FeedUser)
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static


app_name = "user_gallery"

router = routers.SimpleRouter()


router.register(r'photos', PhotoUser)
router.register(r'albums', AlbumsUser)
router.register(r'bookmarks', BookmarksUser)

urlpatterns = [
    path('signup/', SignUpUser.as_view(), name="signup"),
    path('signin/', SignInUser.as_view(), name ="signin"),
    path('photos/<int:photo_id>/comments/<int:comment_id>/', CommentsUser.as_view({'get': 'retrieve','delete': 'destroy'})),
    path('photos/<int:photo_id>/comments/', CommentsUser.as_view({'get': 'list', 'post': 'create'})),
    path('users/me/', UserMe.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'})),
    path('users/<int:pk>/', UserId.as_view()),
    path('users/<int:user_id>/photos/', UserIdPhotos.as_view()),
    path('users/<int:user_id>/albums/', UserIdAlbums.as_view()),
    path('feed/',FeedUser.as_view()),
]


urlpatterns += router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)