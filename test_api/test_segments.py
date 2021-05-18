import pytest
import requests

from api.common.exceptions import ObjectNotFoundError
from test_api.base_test import APIBaseTest


class SegmentBase(APIBaseTest):
    auto_delete: bool = True

    def _delete_segment(self, segment_id: int) -> requests.Response:
        return self.target_api_client.delete_segment(segment_id)

    @pytest.fixture(scope="function")
    def segment(self) -> dict:
        segment_data = self.builder.create_segment_data()

        segment_json = self.target_api_client.post_create_segment(segment_data)
        segment_data['id'] = segment_json['id']

        yield segment_data

        # Удаление сегмента.
        if self.auto_delete:
            self._delete_segment(segment_json['id'])


class TestCaseCreateSegments(SegmentBase):

    @pytest.mark.API
    def test_create_segment(self, segment: dict) -> None:
        get_segment = self.target_api_client.get_segment(segment['id'])

        assert get_segment['id'] == segment['id']
        assert get_segment['name'] == segment['name']


class TestCaseDeleteSegments(TestCaseCreateSegments):
    auto_delete: bool = True

    @pytest.mark.API
    def test_delete_segment(self, segment: dict) -> None:
        super(TestCaseDeleteSegments, self).test_create_segment(segment)
        self.auto_delete = False

        # Удаление сегмента.
        self._delete_segment(segment['id'])

        with pytest.raises(ObjectNotFoundError):
            self.target_api_client.get_segment(segment['id'])
            pytest.fail(f"Segment with id '{segment['id']}' found after delete.")
