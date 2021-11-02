from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth import login
from django.db.models import Count
from .models import User, Album, Photo, Comment, Bookmark
from .permissions import IsOwner, IsNotStaff
from .serializers import (SignUpUserSerializer, SignInSerializer, UserMeSerializer, UserMeRetrieveSerializer,
                          UserIdSerializer, FeedSerializer, AlbumCreateSerializer, AlbumListSerializer,
                          BookmarksCreateSerializer, BookmarksListSerializer, PhotoCreateUpdateSerializer,
                          PhotoListGetSerializer, PhotoUpdateSerializer, CommentsCreateSerializer,
                          CommentsListSerializer)


class UserMe(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsNotStaff]
    serializer_class = UserMeSerializer
    serializer_class_retrieve = UserMeRetrieveSerializer

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return self.serializer_class

        return self.serializer_class_retrieve

    def get_object(self):
        obj = User.objects.get(id=self.request.user.pk)
        return obj


class UserId(generics.RetrieveAPIView):
    # ---------------- Users ID ----------------
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsNotStaff]
    serializer_class = UserIdSerializer


class UserIdPhotos(generics.ListAPIView):
    # ---------------- Users ID Photos----------------
    queryset = Photo.objects.all()
    permission_classes = [IsAuthenticated, IsNotStaff]
    serializer_class = PhotoListGetSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Photo.objects.filter(owner=user_id)


class UserIdAlbums(generics.ListAPIView):
    queryset = Album.objects.all()
    permission_classes = [IsAuthenticated, IsNotStaff]
    serializer_class = AlbumListSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Album.objects.filter(owner=user_id)


class FeedUser(generics.ListAPIView):  # ---------------- Feed ----------------
    queryset = (
        Photo.objects.annotate(comm=Count("comments"), bookma=Count("bookmarks"))
            .order_by("-comm")
            .order_by("-bookma")

    )
    permission_classes = [IsAuthenticated, IsNotStaff]
    serializer_class = FeedSerializer


class SignUpUser(generics.CreateAPIView):  # -----------  Register -------------
    queryset = User.objects.all()
    permission_classes = (IsNotStaff,)
    serializer_class = SignUpUserSerializer


class SignInUser(generics.GenericAPIView):  # -------------------- Login --------------
    queryset = User.objects.all()
    permission_classes = [IsNotStaff]
    serializer_class = SignInSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        try:
            user = User.objects.get(email=email)
        except:
            return Response({"Error": "Email or password incorrect"})
        if not user.check_password(password) or user.is_staff or user.is_superuser:
            return Response({"Error": "Email or password incorrect"})
        login(request, user)
        serializer = SignInSerializer(user)
        return Response(serializer.data)


class AlbumsUser(viewsets.ModelViewSet):
    #  --------------------- Albums --------------------------------
    queryset = Album.objects.all()
    serializer_class = AlbumCreateSerializer
    serializer_class_for_listing = AlbumListSerializer
    permission_classes = [IsAuthenticated, IsOwner, IsNotStaff]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return self.serializer_class

        return self.serializer_class_for_listing

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PhotoUser(viewsets.ModelViewSet):
    # --------------------- Photos --------------------------------
    queryset = Photo.objects.all()
    serializer_class = PhotoCreateUpdateSerializer
    serializer_class_for_listing = PhotoListGetSerializer
    serializer_class_for_update = PhotoUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwner, IsNotStaff]

    def get_serializer_class(self):
        if self.action in ["create"]:
            return self.serializer_class
        if self.action in ["update", "partial_update"]:
            return self.serializer_class_for_update

        return self.serializer_class_for_listing

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.image.delete()
        instance.delete()
        serializer = PhotoListGetSerializer(instance)
        return Response(serializer.data)


class BookmarksUser(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarksCreateSerializer
    permission_classes = [IsAuthenticated, IsOwner, IsNotStaff]
    serializer_class_for_listing = BookmarksListSerializer

    def get_serializer_class(self):
        if self.action in ["create"]:
            return self.serializer_class

        return self.serializer_class_for_listing

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentsUser(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet, ):
    # --------------------- Comments --------------------------------
    queryset = Comment.objects.all()
    serializer_class = CommentsCreateSerializer
    permission_classes = [IsAuthenticated, IsOwner, IsNotStaff]
    serializer_class_for_listing = CommentsListSerializer
    lookup_url_kwarg = "comment_id"

    def get_serializer_class(self):
        if self.action in ["create"]:
            return self.serializer_class

        return self.serializer_class_for_listing

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        photo_id = self.kwargs["photo_id"]
        return Comment.objects.filter(photo_id=photo_id)
