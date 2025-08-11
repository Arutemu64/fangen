import json
import logging
from pathlib import Path

from adaptix import Retort
from requests import Session, HTTPError
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from fangen.cosplay2.models.topic import TopicDTO, TopicWithFieldsDTO
from fangen.cosplay2.models.plan import PlanNodeDTO
from fangen.cosplay2.models.request import RequestDTO
from fangen.cosplay2.models.value import RequestValueDTO

logger = logging.getLogger(__name__)


class Cosplay2Client:
    _cookie_file = Path("./cookies.json")

    def __init__(self, event_name: str):
        self.session = Session()
        self.base_url = f"https://{event_name}.cosplay2.ru/api/"
        self.retort = Retort(strict_coercion=False)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0"
        }

    def auth(self, login: str, password: str) -> bool:
        if self._cookie_file.is_file():
            with open(self._cookie_file, "r") as f:
                cookies_dict = json.load(f)
                self.session.cookies = cookiejar_from_dict(cookies_dict)
            test_url = self.base_url + "events/get_settings"
            test_response = self.session.get(url=test_url, headers=self.headers)
            if test_response.ok:
                logger.info("Вошли через Cookie!")
                return True
            logger.info("Cookie устарели, входим по логину и паролю")
            self.session.cookies.clear()

        login_url = self.base_url + "users/login"
        login_response = self.session.post(
            url=login_url,
            data={"name": login, "password": password},
            headers=self.headers,
        )
        if login_response.ok:
            self.session.cookies = login_response.cookies
            with open(self._cookie_file, "w") as f:
                cookies_dict = dict_from_cookiejar(self.session.cookies)
                json.dump(cookies_dict, f)
            logger.info("Успешно вошли и обновили Cookie!")
            return True
        else:
            try:
                login_response.raise_for_status()
            except HTTPError as e:
                msg = (
                    f"Ошибка входа в Cosplay2 — код {e.response.status_code}. "
                    f"Проверьте корректность данных в конфиге."
                )
                raise HTTPError(msg) from e
            return False

    def get_list(self) -> list[TopicDTO]:
        url = self.base_url + "topics/get_list"
        response = self.session.get(url=url, headers=self.headers)
        data = response.json()
        return self.retort.load(data, list[TopicDTO])

    def get_plan(self) -> list[PlanNodeDTO]:
        url = self.base_url + "events/get_plan"
        response = self.session.get(url=url, headers=self.headers)
        data: str = response.json()["plan"]
        return self.retort.load(json.loads(data), list[PlanNodeDTO])

    def get_all_requests(self) -> list[RequestDTO]:
        url = self.base_url + "topics/get_all_requests"
        response = self.session.get(url=url, headers=self.headers)
        data = response.json()
        return self.retort.load(data, list[RequestDTO])

    def get_all_values(self) -> list[RequestValueDTO]:
        url = self.base_url + "requests/get_all_values"
        response = self.session.get(url=url, headers=self.headers)
        data = response.json()
        return self.retort.load(data, list[RequestValueDTO])

    def get_with_fields(self, topic_url_code: str) -> TopicWithFieldsDTO:
        url = self.base_url + "topics/get_with_fields"
        response = self.session.post(
            url=url, json={"topic_url_code": topic_url_code}, headers=self.headers
        )
        data = response.json()
        return self.retort.load(data, TopicWithFieldsDTO)
