def test_metrics_endpoint_exposes_prometheus_metrics(client):
    # Generate one instrumented request before scraping the registry.
    health_response = client.get("/health")
    assert health_response.status_code == 200

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text
    # Metrics endpoint must not instrument itself and inflate request counts.
    assert 'handler="/metrics"' not in response.text
