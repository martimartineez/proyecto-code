from minio import Minio


class Storage:
    def __init__(self, App=None):
        self._client = None
        if App is not None:
            self.init_app(App)

    def init_app(self, App):
        self._client = Minio(
            App.config["MINIO_SERVER"],
            access_key=App.config["MINIO_ACCESS_KEY"],
            secret_key=App.config["MINIO_SECRET_KEY"],
            secure=App.config.get("MINIO_SECURE", False),
        )

        App.storage = self._client
        return App


storage = Storage()
