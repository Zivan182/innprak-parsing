import script
from unittest.mock import Mock, patch


@patch('script.get_selenium_response')
@patch('script.get_shops')
@patch('script.get_shops_page')
@patch('script.get_price')
@patch('script.get_price_page')
def test_get_product_info(mock_get_price_page, mock_get_price, mock_get_shops_page, mock_get_shops,
                          mock_get_selenium_response):
    mock_get_price_page.return_value = 'price_page'
    mock_get_price.side_effect = [(100, 'RUB'), (1000, 'RUB'), (10000, 'RUB')]

    mock_get_shops_page.return_value = 'shops_page'

    shops1 = [{"quantity": 1, "id": "1", "title": "A", "address": "Москва, DNS-1", "latitude": 1, "longitude": 1,
               "cityName": "Москва", "is_suburb": False}]
    shops2 = [
        {"quantity": 2, "id": "2", "title": "B", "address": "Санкт-Петербург, DNS-2", "latitude": 2, "longitude": 2,
         "cityName": "Санкт-Петербург", "is_suburb": False}]
    shops3 = [{"quantity": 3, "id": "3", "title": "C", "address": "Казань, DNS-3", "latitude": 3, "longitude": 3,
               "cityName": "Казань", "is_suburb": False}]

    mock_get_shops.side_effect = [(shops1, 1), (shops2, 2), (shops3, 3)]

    mock_get_selenium_response.return_value = {"data": {"sku": "artikul"}}

    microdata_request = script.requests.Request()
    microdata_request.url = '/microdata/productId/'
    microdata_request.headers = {'Cookie': 'id=123; city_path=spb;'}
    microdata_request.response = []

    def func(driver, request):
        def f(_):
            driver.requests = [request]
        return f

    mock_driver = Mock(spec=script.uc.Chrome)
    mock_driver.get.side_effect = func(mock_driver, microdata_request)

    url = 'test_url'

    product_info = script.get_product_info(mock_driver, url)

    assert product_info['info_by_region']['Москва']['price'] == 100
    assert product_info['info_by_region']['Москва']['quantity'][0]['title'] == 'A'
    assert product_info['info_by_region']['Санкт-Петербург']['price'] == 1000
    assert product_info['info_by_region']['Санкт-Петербург']['quantity'][0]['title'] == 'B'
    assert product_info['info_by_region']['Казань']['price'] == 10000
    assert product_info['info_by_region']['Казань']['quantity'][0]['title'] == 'C'
    assert mock_get_price.call_args_list == [(('price_page',),), (('price_page',),), (('price_page',),)]
    assert mock_get_shops.call_args_list == [(('shops_page', 'Москва'),), (('shops_page', 'Санкт-Петербург'),),
                                             (('shops_page', 'Казань'),)]
    assert mock_get_price_page.call_args_list == [((microdata_request, 'moscow'),),
                                                  ((microdata_request, 'spb'),),
                                                  ((microdata_request, 'kazan'),)]
    assert mock_get_shops_page.call_args_list == [((script.siteId, script.cityIds['Москва'], 'productId'),),
                                                  ((script.siteId, script.cityIds['Санкт-Петербург'], 'productId'),),
                                                  ((script.siteId, script.cityIds['Казань'], 'productId'),)]
    assert mock_get_selenium_response.call_args_list == [((microdata_request,),)]
    assert mock_driver.get.call_args_list == [((url,),)]
