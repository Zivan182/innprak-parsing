import time
from time import sleep
from seleniumwire.utils import decode
import seleniumwire.undetected_chromedriver as uc
import json
from tqdm.auto import tqdm
import requests


regions = ['Москва', 'Санкт-Петербург', 'Казань']
shops_url = 'https://shops.dns-shop.ru/v1/shops-avail-by-partition'

siteId = "8c2e120b-8732-48a7-8178-0e04d47962d8"
cityIds = {
    "Москва": "30b7c1f3-03fb-11dc-95ee-00151716f9f5",
    "Санкт-Петербург": "566ca284-5bea-11e2-aee1-00155d030b1f",
    "Казань": "55506b55-0565-11df-9cf0-00151716f9f5",
}
city_paths = {
    "Москва": "moscow",
    "Санкт-Петербург": "spb",
    "Казань": "kazan",
}


def create_driver():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.page_load_strategy = 'none'

    driver = uc.Chrome(
        options=chrome_options,
        seleniumwire_options={}
    )
    return driver


def get_price_page(microdata_request, city_path):
    cookie = microdata_request.headers['Cookie'].split(' ')
    for i in range(len(cookie)):
        if 'city_path' in cookie[i]:
            cookie[i] = f'city_path={city_path};'
    headers = dict(microdata_request.headers)
    headers['Cookie'] = ' '.join(cookie)

    response = requests.get(microdata_request.url, headers=headers)

    if response.status_code != 200:
        raise Exception(f'smth wrong with price request: Status Code is {response.status_code}')

    return response.json()


def get_price(price_page):
    price = priceCurrency = None
    if 'data' in price_page.keys() and 'offers' in price_page['data'].keys() \
            and 'price' in price_page['data']['offers'].keys():
        price = price_page['data']['offers']['price']
        priceCurrency = price_page['data']['offers']['priceCurrency']
    return price, priceCurrency


def get_shops_page(siteId, cityId, productId):
    headers = {
        'Origin': 'https://www.dns-shop.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }

    body = {
        "siteId": siteId,
        "cityId": cityId,
        "products": [{"id": productId, "count": 1}],
        "offset": 0,
        "notShowAvails": False,
        "isCheckout": False,
        "locales": "ru",
        "isParentCityNeeded": False,
    }

    response = requests.post(shops_url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception(f'smth wrong with shops request: Status Code is {response.status_code}')

    return response.json()


def get_shops(shops_page, region):
    shops = dict()
    quantity_total = 0
    for shop in shops_page['avail']['products'][0]['branches']:
        if shop['maxCount'] > 0:
            quantity_total += shop['maxCount']
            shops[shop['branchId']] = {'quantity': shop['maxCount']}
    for shop in shops_page['shops']:
        shop_id = shop['id']
        if shop_id not in shops.keys():
            continue
        new_keys = ['id', 'title', 'address', 'latitude', 'longitude', 'cityName']
        for new_key in new_keys:
            shops[shop_id][new_key] = shop[new_key]
        shops[shop_id]['is_suburb'] = (shop['cityName'] != region)

    return list(shops.values()), quantity_total


def get_selenium_response(selenium_request):
    selenium_response = json.loads(decode(selenium_request.response.body,
                                          selenium_request.response.headers.get('Content-Encoding', 'identity')
                                          ).decode('utf-8'))
    return selenium_response


def get_product_info(driver, url):
    product_info = {'url': url}

    try:
        del driver.requests
        driver.get(url)

        microdata_request = None

        waiting_time = 50
        sleep_time = 1
        while microdata_request is None:
            if waiting_time <= 0:
                raise Exception('waiting too long for microdata request')
            waiting_time -= sleep_time
            sleep(sleep_time)
            for i in driver.requests:
                if ('/microdata/' in i.url) and not (i.response is None):
                    microdata_request = i

        productId = microdata_request.url.split('/')[-2]

        microdata_response = get_selenium_response(microdata_request)

        product_info['artikul'] = microdata_response['data']['sku']
        product_info['info_by_region'] = {}

        for region in regions:
            price_page = get_price_page(microdata_request, city_paths[region])
            price, priceCurrency = get_price(price_page)

            shops_page = get_shops_page(siteId, cityIds[region], productId)
            shops, quantity_total = get_shops(shops_page, region)

            product_info['info_by_region'][region] = {
                'price': price, 'priceCurrency': priceCurrency,
                'quantity': shops, 'quantity_total': quantity_total
            }
    except Exception as e:
        product_info['errors'] = e
    finally:
        return product_info


def get_products_info(urls):
    attempts_count = 2
    total_start_time = time.time()
    products_info = []
    driver = create_driver()
    for url in tqdm(urls):
        product_info = None
        for attempt in range(attempts_count):
            product_info = get_product_info(driver, url)
            if 'errors' not in product_info.keys():
                break
            print(url, ': error, attempt:', attempt + 1)
        products_info.append(product_info)
    driver.quit()
    print("--- Total: %s seconds ---" % (time.time() - total_start_time))
    return products_info


def save_json(products_info):
    ans = {}
    for product in products_info:
        if 'url' in product.keys():
            ans[product['url']] = product

    with open('ans.txt', 'w', encoding='utf-8') as outfile:
        json.dump(ans, outfile, ensure_ascii=False)
