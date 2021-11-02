from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, Album, Bookmark, Photo, Comment


class SignUpUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    #first_name = serializers.CharField(allow_blank=True, required=True)
    #last_name = serializers.CharField(allow_blank=True, required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class SignInSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ("id", "email", "password")


class UserIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "created_on", "updated_on")


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class UserMeRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "created_on", "updated_on")


class FeedSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    album = serializers.StringRelatedField()
    comments = serializers.StringRelatedField(many=True)
    bookmarks = serializers.StringRelatedField(many=True)

    class Meta:
        model = Photo
        fields = (
            "id",
            "description",
            "album",
            "image",
            "owner",
            "comments",
            "bookmarks",
            "created_on",
            "updated_on",
        )


class AlbumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ("id", "name")


class AlbumListSerializer(serializers.ModelSerializer):
    photos = serializers.StringRelatedField(many=True)
    owner = serializers.StringRelatedField()

    class Meta:
        model = Album
        fields = (
            "id",
            "owner",
            "name",
            "photos",
            "created_on",
            "updated_on",
        )


class BookmarksCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ("id", "photo")

    def validate_photo(self, value):
        request = self._context["request"]
        current_user_id = request.user.pk
        if value.owner_id == current_user_id:
            raise ValidationError("It's your photo")
        if Bookmark.objects.filter(photo=value.id, owner=current_user_id).exists():
            raise ValidationError("All ready exists")

        return value


class BookmarksListSerializer(serializers.ModelSerializer):
    photo = serializers.StringRelatedField()
    owner = serializers.StringRelatedField()

    class Meta:
        model = Bookmark
        fields = ("id", "photo", "owner", "created_on")


class PhotoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ("id", "description", "album", "image")

    def validate_album(self, value):
        request = self._context["request"]
        current_user = request.user
        if not Album.objects.filter(id=value.pk, owner=current_user).exists():
            raise ValidationError("It's not your album")

        return value


class PhotoListGetSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    comments = serializers.StringRelatedField(many=True)
    bookmarks = serializers.StringRelatedField(many=True)
    album = serializers.StringRelatedField()

    class Meta:
        model = Photo
        fields = (
            "id",
            "description",
            "album",
            "image",
            "owner",
            "comments",
            "bookmarks",
            "created_on",
            "updated_on",
        )


class PhotoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ("id", "description")


class CommentsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "text", "photo")


class CommentsListSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    photo = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "photo",
            "owner",
            "created_on",
            "updated_on",
        )
