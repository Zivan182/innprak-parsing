import script
from unittest.mock import patch


def test_get_price_with_price():
    price_page = {'data': {'offers': {'price': 100, 'priceCurrency': 'RUB'}}}
    price, priceCurrency = script.get_price(price_page)
    assert price == 100
    assert priceCurrency == 'RUB'


def test_get_price_without_price():
    price_page = {'data': {}}
    price, priceCurrency = script.get_price(price_page)
    assert price is None
    assert priceCurrency is None


@patch('script.requests.get')
def test_get_price_page_with_good_request(mock_requests_get):
    response = script.requests.Response()
    response.status_code = 200
    utf_string = '{"data": {"offers": {"price": 100, "priceCurrency": "RUB"}}}'
    bytes_string = utf_string.encode('utf-8')
    response._content = bytes_string
    mock_requests_get.return_value = response

    microdata_request = script.requests.Request()
    microdata_request.url = 'test_url'
    microdata_request.headers = {'Cookie': 'id=123; city_path=spb;'}
    city_path = 'moscow'

    price_page = script.get_price_page(microdata_request, city_path)

    assert mock_requests_get.call_args == (('test_url',), {'headers': {'Cookie': 'id=123; city_path=moscow;'}})
    assert price_page['data']['offers']['price'] == 100
    assert price_page['data']['offers']['priceCurrency'] == 'RUB'


@patch('script.requests.get')
def test_get_price_page_with_bad_request(mock_requests_get):
    response = script.requests.Response()
    response.status_code = 403
    mock_requests_get.return_value = response

    microdata_request = script.requests.Request()
    microdata_request.url = 'test_url'
    microdata_request.headers = {'Cookie': 'id=123; city_path=spb;'}
    city_path = 'moscow'

    try:
        script.get_price_page(microdata_request, city_path)
        assert False
    except Exception as e:
        assert e.args[0] == 'smth wrong with price request: Status Code is 403'

    assert mock_requests_get.call_args == (('test_url',), {'headers': {'Cookie': 'id=123; city_path=moscow;'}})


def test_get_shops_in_stock():
    shops_page = {
        'shops': [
            {'id': '1', 'title': 'A', 'address': 'Москва, DNS-1', 'latitude': 1, 'longitude': 1, 'cityName': 'Москва'},
            {'id': '2', 'title': 'A', 'address': 'Москва, DNS-2', 'latitude': 2, 'longitude': 2, 'cityName': 'Москва'}
        ],
        'avail': {
            'products': [
                {'branches': [
                    {'maxCount': 10, 'branchId': '2'}
                ]
                }
            ]
        }
    }

    region = 'Москва'

    expected_keys = ['quantity', 'id', 'title', 'address', 'latitude', 'longitude', 'cityName', 'is_suburb']

    shops_list, quantity_total = script.get_shops(shops_page, region)
    assert len(shops_list) == 1
    assert all(key in shops_list[0].keys() for key in expected_keys)
    assert quantity_total == 10


def test_get_shops_out_of_stock():
    shops_page = {
        'shops': [
            {'id': '1', 'title': 'A', 'address': 'Москва, DNS-1', 'latitude': 1, 'longitude': 1, 'cityName': 'Москва'},
            {'id': '2', 'title': 'A', 'address': 'Москва, DNS-2', 'latitude': 2, 'longitude': 2, 'cityName': 'Москва'}
        ],
        'avail': {'products': [{'branches': []}]}
    }

    region = 'Москва'

    shops_list, quantity_total = script.get_shops(shops_page, region)
    assert len(shops_list) == 0
    assert quantity_total == 0


@patch('script.requests.post')
def test_get_shops_page_good_request(mock_requests_post):
    response = script.requests.Response()
    response.status_code = 200
    utf_string = '''{
        "shops": [
            {"id": "1", "title": "A", "address": "Москва, DNS-1", "latitude": 1, "longitude": 1, "cityName": "Москва"}
        ],
        "avail": {
            "products": [
                {"branches": [
                    {"maxCount": 10, "branchId": "2"}
                ]
                }
            ]
        }
    }'''
    bytes_string = utf_string.encode('utf-8')
    response._content = bytes_string
    mock_requests_post.return_value = response

    siteId = cityId = productId = '1'

    shops_page = script.get_shops_page(siteId, cityId, productId)

    expected_url = 'https://shops.dns-shop.ru/v1/shops-avail-by-partition'

    expected_headers = {
        'Origin': 'https://www.dns-shop.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }

    expected_body = {
        "siteId": siteId,
        "cityId": cityId,
        "products": [{"id": productId, "count": 1}],
        "offset": 0,
        "notShowAvails": False,
        "isCheckout": False,
        "locales": "ru",
        "isParentCityNeeded": False,
    }

    assert mock_requests_post.call_args == ((expected_url,), {'headers': expected_headers, 'json': expected_body})
    assert shops_page['shops'][0]['id'] == '1'
    assert shops_page['avail']['products'][0]['branches'][0]['maxCount'] == 10


@patch('script.requests.post')
def test_get_shops_page_bad_request(mock_requests_post):
    response = script.requests.Response()
    response.status_code = 403
    mock_requests_post.return_value = response

    siteId = cityId = productId = '1'

    try:
        script.get_shops_page(siteId, cityId, productId)
        assert False
    except Exception as e:
        assert e.args[0] == 'smth wrong with shops request: Status Code is 403'

    expected_url = 'https://shops.dns-shop.ru/v1/shops-avail-by-partition'

    expected_headers = {
        'Origin': 'https://www.dns-shop.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }

    expected_body = {
        "siteId": siteId,
        "cityId": cityId,
        "products": [{"id": productId, "count": 1}],
        "offset": 0,
        "notShowAvails": False,
        "isCheckout": False,
        "locales": "ru",
        "isParentCityNeeded": False,
    }

    assert mock_requests_post.call_args == ((expected_url,), {'headers': expected_headers, 'json': expected_body})
