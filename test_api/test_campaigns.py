import os
import pytest

from test_api.base_test import APIBaseTest


class CampaignsBase(APIBaseTest):

    def _get_ids(self, root_path: str) -> dict:
        path_images = os.path.join(root_path, 'tmp', 'images')

        images_id = self.target_api_client.post_send_image(os.path.join(path_images, '240x400.jpg'))

        return {
            'images': {
                'id_static': images_id['id_static'],
                'id_mediateka': images_id['id_mediateka']
            },
            'primary_url': self.target_api_client.get_campaign_url_id("https://mail.ru/")
        }

    def _delete_images(self, id_mediateka: int) -> None:
        self.target_api_client.delete_image(id_mediateka)

        # Получаем заново изображение.
        img_response_json = self.target_api_client.get_image(id_mediateka, expected_status=404)

        assert img_response_json['error']['code'] == 'not_found'
        assert img_response_json['error']['message'] == 'Resource not found'
        assert img_response_json['error']['resource'] == 'UserContent'

    def _delete_campaign(self, campaign_id: int) -> None:
        self.target_api_client.delete_campaign(campaign_id)

        # Проверка удаления кампании.
        response_campaign = self.target_api_client.get_campaign(campaign_id)

        assert response_campaign['id'] == campaign_id
        assert response_campaign['status'] == "deleted"

    def _check_create_campaign(self, campaign_data: dict) -> None:
        get_campaign = self.target_api_client.get_campaign(campaign_data['_id'])

        assert get_campaign['id'] == campaign_data['_id']
        assert get_campaign['name'] == campaign_data['name']
        assert get_campaign['status'] == campaign_data['_status']

    @pytest.fixture(scope="function")
    def campaign(self, root_path: str) -> dict:
        ids = self._get_ids(root_path)
        campaign_data = self.builder.create_campaign_data(ids)

        # Создание кампании.
        campaign_json = self.target_api_client.post_create_campaign(campaign_data)
        campaign_data['_id'] = campaign_json['id']
        campaign_data['_status'] = 'active'

        yield campaign_data

        # Удаление изображения в кампании по ID.
        self._delete_images(ids['images']['id_mediateka'])

        # Удаление кампании.
        self._delete_campaign(campaign_data['_id'])


class TestCaseCampaigns(CampaignsBase):

    @pytest.mark.API
    def test_post_create_campaign(self, campaign: dict) -> None:
        self._check_create_campaign(campaign)
