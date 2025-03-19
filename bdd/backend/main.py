from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import yaml
from pathlib import Path
import uvicorn

app = FastAPI(title="Karate BDD Automation Generator")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class LLMRequest(BaseModel):
    messages: List[Message]
    max_new_tokens: int = 200
    temperature: float = 0.7

class EndpointConfig(BaseModel):
    jiraStory: str
    requestData: str
    responseData: str
    selected: bool

class GenerateTestRequest(BaseModel):
    endpoints: Dict[str, EndpointConfig]
    openApiSpec: dict

@app.post("/parse-openapi")
async def parse_openapi(file: UploadFile):
    try:
        content = await file.read()
        if file.filename.endswith(('.yaml', '.yml')):
            spec = yaml.safe_load(content)
        else:
            spec = json.loads(content)
        
        # Validate the OpenAPI spec structure
        if 'paths' not in spec:
            raise HTTPException(status_code=400, detail="Invalid OpenAPI specification: 'paths' field is required")
        
        return {"spec": spec}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-tests")
async def generate_tests(request: GenerateTestRequest):
    try:
        # Filter selected endpoints
        selected_endpoints = {
            path: config for path, config in request.endpoints.items()
            if config.selected
        }
        
        # Generate test cases for each selected endpoint
        test_cases = {}
        for path, config in selected_endpoints.items():
            test_cases[path] = generate_karate_test(
                path,
                request.openApiSpec['paths'][path],
                config
            )
        
        return {"testCases": test_cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_llm(request: LLMRequest):
    try:
        # Mock LLM response for development
        # In production, this would call your local LLM endpoint
        return {
            "response": "Generated test cases based on JIRA story and API specification.",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_karate_test(path: str, path_spec: dict, config: EndpointConfig) -> str:
    # Extract HTTP methods and their specifications
    methods = {
        method: spec for method, spec in path_spec.items()
        if method.lower() in ['get', 'post', 'put', 'delete', 'patch']
    }
    
    feature_template = f"""Feature: {path} API Tests
    
Background:
    * url baseUrl
    * def requestData = {config.requestData or '{}'}
    * def expectedResponse = {config.responseData or '{}'}
    """
    
    # Generate scenarios for each HTTP method
    scenarios = []
    for method, spec in methods.items():
        scenario = f"""
Scenario: {method.upper()} {path}
    Given path '{path}'
    And request requestData
    When method {method}
    Then status 200
    And match response == expectedResponse"""
        scenarios.append(scenario)
    
    return feature_template + '\n'.join(scenarios)

@app.post("/setup-wiremock")
async def setup_wiremock(request: GenerateTestRequest):
    try:
        # Generate WireMock stubs for selected endpoints
        stubs = []
        for path, config in request.endpoints.items():
            if config.selected:
                stub = {
                    "request": {
                        "url": path,
                        "method": "ANY"  # You might want to be more specific based on the OpenAPI spec
                    },
                    "response": {
                        "status": 200,
                        "jsonBody": json.loads(config.responseData) if config.responseData else {}
                    }
                }
                stubs.append(stub)
        
        return {"stubs": stubs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)