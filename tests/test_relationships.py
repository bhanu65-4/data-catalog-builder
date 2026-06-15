from catalog_utils import detect_relationships


def test_detect_shared_column_relationship():
    tables = [
        {
            'name': 'customers',
            'row_count': 20,
            'columns': [{'name': 'customer_id'}, {'name': 'email'}],
        },
        {
            'name': 'orders',
            'row_count': 30,
            'columns': [{'name': 'order_id'}, {'name': 'customer_id'}],
        },
    ]
    relationships = detect_relationships(tables)
    assert len(relationships) == 1
    assert relationships[0]['parent'] == 'customers'
    assert relationships[0]['child'] == 'orders'
    assert relationships[0]['column'] == 'customer_id'
