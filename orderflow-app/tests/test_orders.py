def test_create_order(client):
    payload = {
        "customer_id": "CUST-1001",
        "product": "Laptop",
        "quantity": 1,
        "amount": 75000,
    }

    response = client.post("/api/v1/orders", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["order_id"].startswith("ORD-")
    assert body["customer_id"] == "CUST-1001"
    assert body["status"] == "CREATED"
    assert body["amount"] == "75000.00"


def test_list_get_update_and_delete_order(client):
    create_response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": "CUST-1002",
            "product": "Keyboard",
            "quantity": 2,
            "amount": 2500,
        },
    )
    order_id = create_response.json()["order_id"]

    list_response = client.get("/api/v1/orders")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(f"/api/v1/orders/{order_id}")
    assert get_response.status_code == 200
    assert get_response.json()["order_id"] == order_id

    update_response = client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "CONFIRMED"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "CONFIRMED"

    delete_response = client.delete(f"/api/v1/orders/{order_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/orders/{order_id}")
    assert missing_response.status_code == 404


def test_invalid_order_is_rejected(client):
    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": "CUST-1003",
            "product": "Mouse",
            "quantity": 0,
            "amount": 1000,
        },
    )

    assert response.status_code == 422
