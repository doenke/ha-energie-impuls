class EnergyImpulsSession:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None

    def get_token(self):
        response = requests.post(LOGIN_URL, json={
            "username": self.username,
            "password": self.password
        })

        if response.status_code in (200, 201, 204):
            json_data = response.json()
            self.token = json_data.get("access")
            if self.token:
                _LOGGER.info(f"Neuer Token erhalten: {self.token}")
            else:
                _LOGGER.error(f"Antwort ohne Token: {json_data}")
        else:
            _LOGGER.error(f"Login fehlgeschlagen ({response.status_code}): {response.text}")
            raise Exception("Login fehlgeschlagen")

    def get_data(self):
        if not self.token:
            self.get_token()
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(DATA_URL, headers=headers)
        if response.status_code == 401:
            self.get_token()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(DATA_URL, headers=headers)
        if response.status_code in (200, 201, 204):
            return response.json()
        raise Exception("Fehler bei API-Antwort")

    def get_wallbox_data(self):
        if not self.token:
            self.get_token()

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(WALLBOX_URL, headers=headers)

        if response.status_code == 401:
            self.get_token()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(WALLBOX_URL, headers=headers)

        if response.status_code in (200, 201, 204):
            try:
                json_data = response.json()
                if isinstance(json_data, list) and json_data:
                    return json_data[0]
                else:
                    raise Exception("Wallbox-Antwort war leer oder kein Array.")
            except Exception as e:
                raise Exception(f"Fehler beim Parsen der Wallbox-Antwort: {e}")
        else:
            raise Exception(f"Wallbox-API Fehler: {response.status_code} → {response.text}")
