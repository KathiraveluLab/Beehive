# **Testing Guide for Beehive**  
This document provides guidelines for running test cases in the project.  

## **1. Setting Up the Test Environment**  
Before running the tests, ensure you have a virtual environment set up and all dependencies installed.  

## **2. Running the Tests**  

### **Run All Test Cases**  
To execute all test cases, run:  

```bash
pytest
```

### **Run Specific Test File**  
To run tests from a specific file, use:  

```bash
pytest tests/test_example.py
```

### **Run a Single Test Case**  
To run a specific test function, use:  

```bash
pytest tests/test_example.py::test_name
```

### **Run Tests with Detailed Output**  
To see more details on test execution, use:  

```bash
pytest -v
```

### **Run Tests with Coverage**  
To check test coverage, install `pytest-cov` if not already installed:  

```bash
pip install pytest-cov
```
Then run:  

```bash
pytest --cov=app
```


## **4. Debugging Failing Tests**  

Some Common HTTP codes which you will encounter while running the tests
- **200 (OK)** – The request was successful, and the page loaded correctly.  
- **201 (Created)** – A new resource was successfully created (used for APIs that create data).  
- **204 (No Content)** – The request was successful, but there’s no response body (common in DELETE requests).
- **302 (Redirect):** If a page redirects, ensure authentication is handled. Log in before accessing protected routes.
- **400 (Bad Request)** – The request was malformed or missing required parameters.
- **401 (Unauthorized)** – Authentication is required but missing or incorrect. 
- **404 (Not Found):** If a route returns 404, check if it exists in the Flask app using `flask routes`.
- **405 (Method Not Allowed)** – The HTTP method (e.g., GET, POST, PUT) is not allowed for this route.
- **422 (Unprocessable Entity)** – The request was formatted correctly but contains invalid data (e.g., missing required fields).
- **500 (Server Error):** Check logs for issues like missing database tables or incorrect request handling.
- **502 (Bad Gateway)** – The server received an invalid response from an upstream service.  
- **503 (Service Unavailable)** – The server is temporarily down or overloaded.   
- **504 (Gateway Timeout)** – The request took too long to process, often due to slow external APIs.   


## **5. Additional Notes**  

- Ensure your database is set up correctly before running tests.   
- Run tests in a virtual environment to avoid dependency conflicts.  
