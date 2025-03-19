import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_parse_openapi_valid_json():
    # Test parsing valid OpenAPI JSON
    json_content = '''
    {
        "openapi": "3.0.0",
        "paths": {
            "/test": {
                "get": {
                    "summary": "Test endpoint"
                }
            }
        }
    }
    '''
    response = client.post(
        "/parse-openapi",
        files={"file": ("test.json", json_content, "application/json")}
    )
    assert response.status_code == 200
    assert "spec" in response.json()

def test_generate_tests():
    # Test generating Karate BDD tests
    request_data = {
        "endpoints": {
            "/test": {
                "jiraStory": "TEST-123",
                "requestData": "{}",
                "responseData": "{}",
                "selected": True
            }
        },
        "openApiSpec": {
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint"
                    }
                }
            }
        }
    }
    response = client.post("/generate-tests", json=request_data)
    assert response.status_code == 200
    assert "testCases" in response.json()

def test_setup_wiremock():
    # Test WireMock stub generation
    request_data = {
        "endpoints": {
            "/test": {
                "jiraStory": "TEST-123",
                "requestData": "{}",
                "responseData": '{"status": "success"}',
                "selected": True
            }
        },
        "openApiSpec": {
            "paths": {
                "/test": {
                    "get": {}
                }
            }
        }
    }
    response = client.post("/setup-wiremock", json=request_data)
    assert response.status_code == 200
    assert "stubs" in response.json()