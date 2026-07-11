import json
import logging

from adaptix import Retort
from requests import Session

from fangen.cosplay2.models.plan import PlanNodeDTO
from fangen.cosplay2.models.request import RequestDTO
from fangen.cosplay2.models.topic import TopicDTO, TopicWithFieldsDTO
from fangen.cosplay2.models.value import RequestValueDTO

logger = logging.getLogger(__name__)


class Cosplay2Client:
    def __init__(
        self, session: Session, api_key: str, api_secret: str, event_name: str
    ) -> None:
        self.session = session
        self.base_url = f"https://{event_name}.cosplay2.ru/api/"
        self.headers = {
            "X-API-Key": f"{api_key}",
            "X-API-Secret": f"{api_secret}",
        }
        self.retort = Retort(strict_coercion=False)

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
