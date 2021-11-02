from test_plus import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models import *
from ..views import *
from ..serializers import *
from django.core.files import File


class PhotosTests(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        # ------------ create user -----------------
        cls.user_set = User.objects.create(
            email="test_set@user.com", username="test_user_set"
        )
        cls.user_set.set_password("12345678q1")
        cls.user_set.save()

        # ------------- Create album -----------
        cls.album_set = Album.objects.create(name="TestAlbum_set", owner=cls.user_set)
        # --------------- Create photo in album ---------------
        path_to_image = (
            "user_gallery/tests/test_photo/Screenshot from 2021-05-05 13-07-56.png"
        )
        cls.f = File(open(path_to_image, "rb"))
        cls.photo1_set = Photo.objects.create(
            description="test_description_set",
            album=cls.album_set,
            image=cls.f,
            owner=cls.user_set,
        )
        Comment.objects.create(
            text="comment to photo1_set", owner=cls.user_set, photo=cls.photo1_set
        )

    def setUp(self) -> None:

        url = "/api/signin/"
        data = {"email": "test_set@user.com", "password": "12345678q1"}
        self.user_set1 = self.client.post(url, data, format="json")
        self.album_set1 = Album.objects.get(owner=self.user_set1.json()["id"])
        self.photo1_set = Photo.objects.get(owner=self.user_set1.json()["id"])

    def test_user_signup(self):  # ----------- Test Users  ---------------
        # POST /api/signup/
        # --------------- create user -----------------
        url = "/api/signup/"
        data = {
            "email": "test@user.com",
            "password": "12345678q1",
            "password2": "12345678q1",
            "username": "test_user",
            "first_name": "",
            "last_name": "",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            User.objects.get(username=data["username"]).username, "test_user"
        )

        # ------------ BAD create user ------------------- только уникальные email  и  username  ---------------
        url = "/api/signup/"
        data = {
            "email": "test@user.com",
            "password": "12345678q1",
            "password2": "12345678q1",
            "username": "test_user",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        bad_response = {
            "username": [
                "A user with that username already exists."
            ],
            "email": [
                "user with this email already exists."
            ]
        }
        self.assertEqual(response.json(), bad_response)

    def test_signin(self):
        url = "/api/signup/"
        data = {
            "email": "test@user.com",
            "password": "12345678q1",
            "password2": "12345678q1",
            "username": "test_user",
            "first_name":"",
            "last_name":"",
        }
        response_sing_up = self.client.post(url, data, format="json")
        self.assertEqual(response_sing_up.status_code, status.HTTP_201_CREATED)

        #   POST /api/sigin/
        # ----- singin -------------
        url = "/api/signin/"
        data = {"email": "test@user.com", "password": "12345678q1"}
        response_sing_in = self.client.post(url, data, format="json")
        self.assertEqual(response_sing_in.status_code, status.HTTP_200_OK)
        self.assertEqual(response_sing_in.json()['id'],response_sing_up.json()['id'])
        self.assertEqual(response_sing_in.json()['email'], response_sing_up.json()['email'])

        # BAD SING_IN
        data = {"email": "test_bad@user.com", "password": "12345678q1"}  # BAD EMAIL
        response_sing_in = self.client.post(url, data, format="json")
        bad_response = {
            "Error": "User or password incorrect"
        }
        self.assertEqual(response_sing_in.json(), bad_response)

        data = {"email": "test@user.com", "password": "bad_password"}  # BAD PASSWORD
        response_sing_in = self.client.post(url, data, format="json")
        bad_response = {
            "Error": "User or password incorrect"
        }
        self.assertEqual(response_sing_in.json(), bad_response)

    def test_user_me(self):  #  GET, PUT, PATCH /api/users/me/
        url = "/api/users/me/"
        # -------------- User ME GET -------------
        user_me = self.client.get(url, format="json")
        self.assertEqual(user_me.status_code, 200)
        self.assertEqual(user_me.json()['email'], "test_set@user.com")
        self.assertEqual(user_me.json()['username'], "test_user_set")

        # --------------- User ME PUT /api/users/me/----------
        data = {
            "first_name": "User",
            "last_name": "ME",
        }
        user_me_put = self.client.put(url, data, format="json")
        self.assertEqual(user_me_put.status_code, 200)
        self.assertEqual(user_me_put.json(), {'first_name': 'User', 'last_name': 'ME'})


    def test_user_albums(self):  #  GET /api/users/{user_id}/albums/
        # -------------  User get albums -------------------------
        url = "/api/users/{0}/albums/".format(self.user_set1.json()["id"])
        user_albums_get = self.client.get(url, format="json")
        albums_user_db = Album.objects.filter(owner=self.user_set1.json()["id"])
        serializer = AlbumListSerializer(albums_user_db, many=True)
        self.assertEqual(user_albums_get.json()['results'], serializer.data)

    def test_user_photos(self):  # GET /api/users/{user_id}/photos/
        # -------------  User get photos -------------------------
        url = "/api/users/{0}/photos/".format(self.user_set1.json()["id"])
        user_photos = self.client.get(url)
        self.assertEqual(user_photos.status_code, 200)
        user_photos_db = Photo.objects.filter(owner=self.user_set1.json()["id"])
        self.assertEqual(user_photos.json()['count'], user_photos_db.count())

    def test_albums(self):  # GET, POST /api/albums/      ----- Test Albums --------------
        # ----- POST  create album ----
        url = "/api/albums/"
        data = {"name": "TestAlbum"}
        album = self.client.post(url, data, format="json")
        self.assertEqual(album.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Album.objects.get(name=data["name"]).name, "TestAlbum")

        # ------------- GET list albums ------------
        url = "/api/albums/"
        all_albums = self.client.get(url)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        albums = Album.objects.all()
        serializer = AlbumListSerializer(albums, many=True)
        #print(all_albums.json()['results'])
        #print(serializer.data)
        self.assertEqual(all_albums.json()['results'], serializer.data)

    def test_album_id(self):  #  GET, PUT, PATCH, DELETE /api/albums/{album_id}/

        # ---------- GET album ------------
        url = "/api/albums/{0}/".format(self.album_set1.id)
        self.album_set1_get = self.client.get(url, format="json")
        self.assertEqual(self.album_set1_get.status_code, 200)

        # ---------- PUT album_id -----------
        url = "/api/albums/{0}/".format(self.album_set1.id)
        data = {"name": "name_PUT"}
        self.album_set1_put = self.client.put(url, data, format="json")
        self.assertEqual(self.album_set1_put.json()["name"], "name_PUT")

        # ------ Delete album - --------------
        url = "/api/albums/{0}/".format(self.album_set1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_photo(self):  # GET, POST /api/photos/ ---------- Test photos --
        # ----------- create photo in album  ---- POST---------------
        url = "/api/photos/"
        path_to_image = (
            "user_gallery/tests/test_photo/Screenshot from 2021-05-05 13-07-56.png"
        )
        f = File(open(path_to_image, "rb"))
        data = {
            "description": "test_description",
            "album": self.album_set.pk,
            "image": f,
        }
        self.photo = self.client.post(url, data)  # , format="json")
        self.assertEqual(self.photo.status_code, status.HTTP_201_CREATED)

        # ----------Photos List -----------------
        url = "/api/photos/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_photo_id(self):  # GET, PUT, PATCH, DELETE /api/photos/{photo_id}/
        # -------------  GET --------------
        url = "/api/photos/{0}/".format(self.photo1_set.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ------------ PUT ---------------
        url = "/api/photos/{0}/".format(self.photo1_set.id)
        data = {"description": "photo_test_put"}
        photo_put = self.client.put(url, data, format="json")
        self.assertEqual(
            photo_put.json()["description"], "photo_test_put"
        )  #'.status_code, status.HTTP_200_OK)

        # ----------------- destroy photo -----------------
        url = "/api/photos/{0}/".format(self.photo1_set.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comments(self):  # --------------- Test Comments -------------
        # ---------------- Create comments -------------- POST /api/photos/{photo_id}/comments/
        url = "/api/photos/{0}/comments/".format(self.photo1_set.id)
        data = {"text": "Comment1 to photo1", "photo": self.photo1_set.id}
        self.comment1 = self.client.post(url, data, format="json")
        self.assertEqual(self.comment1.status_code, status.HTTP_201_CREATED)

        # --------------- Get list comments -------------- GET /api/photos/{photo_id}/comments/
        url = "/api/photos/{0}/comments/".format(self.photo1_set.id)
        self.comments = self.client.get(url)
        self.assertEqual(self.comments.status_code, status.HTTP_200_OK)

        # ------------- Delete comment -------------- DELETE /api/photos/{photo_id}/comments/{comment_id}/
        url = "/api/photos/{0}/comments/{1}/".format(
            self.photo1_set.id, self.comment1.json()["id"]
        )
        self.comment1 = self.client.delete(url)
        self.assertEqual(self.comment1.status_code, status.HTTP_204_NO_CONTENT)

    def test_feed(self):  # ----------- Test Feed --------------

        # ------------------ Get Feed ---------------------
        url = "/api/feed/"
        response = self.client.get(url)
        #print("FEED: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bookmarks(self):  # ------------- Bookmarks ---------------------

        # GET api/bookmarks/
        # --------------- add bookmsrks --------------------
        # --------- Создаем второго юзера и добавляем в закладки фото первого юзера

        # ------------ create and login user --------
        self.user2 = User.objects.create(email="test2@user.com", username="test_user2")
        self.user2.set_password("12345678q1")
        self.user2.save()
        url = "/api/signin/"
        data = {"email": "test2@user.com", "password": "12345678q1"}
        self.client.post(url, data, format="json")

        # POST api/bookmarks/
        # ---------------- create bookmark ---------------
        url = "/api/bookmarks/"
        data = {"photo": self.photo1_set.id}
        self.bookmarks1 = self.client.post(url, data, format="json")
        self.assertEqual(self.bookmarks1.status_code, status.HTTP_201_CREATED)

        # ----------------- get list bookmarks  -------------------
        url = "/api/bookmarks/"
        self.bookmarks = self.client.get(url)
        self.assertEqual(self.bookmarks.status_code, status.HTTP_200_OK)

        # --------------- GET Bookmark -------- GET   /api/bookmarks/{id}/
        url = "/api/bookmarks/{0}/".format(self.bookmarks1.json()["id"])
        self.bookmarks1 = self.client.get(url)
        self.assertEqual(self.bookmarks.status_code, status.HTTP_200_OK)

        # ----------------- delete bookmark ----- delete   /api/bookmarks/{id}/
        url = "/api/bookmarks/{0}/".format(self.bookmarks1.json()["id"])
        self.bookmarks1 = self.client.delete(url)
        self.assertEqual(self.bookmarks1.status_code, status.HTTP_204_NO_CONTENT)
