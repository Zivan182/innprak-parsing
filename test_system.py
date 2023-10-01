import script
import pandas as pd


def test_get_products_info():
    urls = pd.read_csv("dns_test_product_feed.csv")
    sample_size = 5
    urls_test = urls.sample(n=sample_size)['product_url']

    expected_keys = ['url', 'artikul', 'info_by_region']
    expected_regions = ['Москва', 'Санкт-Петербург', 'Казань']

    products_info = script.get_products_info(urls_test)

    assert len(products_info) == sample_size
    for product_info in products_info:
        assert len(product_info.keys()) == len(expected_keys)
        assert all(key in product_info.keys() for key in expected_keys)
        assert all(region in product_info['info_by_region'].keys() for region in expected_regions)
