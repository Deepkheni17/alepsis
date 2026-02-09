"""
Example API Usage Script

This script demonstrates how to use the Invoice Processing API
with various client libraries and methods.

Prerequisites:
- API must be running (uvicorn app.main:app --reload)
- Install requests: pip install requests
"""

import requests
import json
from pathlib import Path


def example_upload_with_requests():
    """Example using requests library"""
    print("\n=== Example 1: Using requests library ===")
    
    # API endpoint
    url = "http://127.0.0.1:8000/upload-invoice"
    
    # For testing, we can create a dummy file or use a real invoice
    # This example assumes you have a file called "test_invoice.pdf"
    # You can create any file for testing (even a .txt renamed to .pdf)
    
    # Create a test file for demonstration
    test_file_path = "test_invoice.txt"
    with open(test_file_path, "w") as f:
        f.write("""
        INVOICE
        ABC Corporation
        Invoice Number: INV-2024-001234
        Date: 2024-01-15
        
        Subtotal: $3,000.00
        Tax (8.5%): $255.00
        TOTAL DUE: $3,255.00
        Currency: USD
        """)
    
    # Upload the file
    with open(test_file_path, "rb") as f:
        files = {"file": (test_file_path, f, "application/pdf")}
        response = requests.post(url, files=files)
    
    # Print response
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    # Clean up
    Path(test_file_path).unlink()


def example_health_check():
    """Example health check"""
    print("\n=== Example 2: Health Check ===")
    
    url = "http://127.0.0.1:8000/health"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))


def example_root_endpoint():
    """Example root endpoint"""
    print("\n=== Example 3: Root Endpoint ===")
    
    url = "http://127.0.0.1:8000/"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))


def example_with_curl():
    """Print cURL command examples"""
    print("\n=== Example 4: cURL Commands ===")
    
    print("\n1. Upload invoice:")
    print("""
curl -X POST "http://127.0.0.1:8000/upload-invoice" \\
  -H "accept: application/json" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@invoice.pdf"
    """)
    
    print("\n2. Health check:")
    print("""
curl -X GET "http://127.0.0.1:8000/health" \\
  -H "accept: application/json"
    """)


def example_expected_responses():
    """Print expected response formats"""
    print("\n=== Example 5: Expected Response Formats ===")
    
    print("\nSuccess Response:")
    success_response = {
        "success": True,
        "extracted_data": {
            "vendor_name": "ABC Corporation",
            "invoice_number": "INV-2024-001234",
            "invoice_date": "2024-01-15",
            "subtotal": 3000.0,
            "tax": 255.0,
            "total_amount": 3255.0,
            "currency": "USD"
        },
        "validation": {
            "is_valid": True,
            "errors": [],
            "warnings": []
        },
        "processing_notes": None
    }
    print(json.dumps(success_response, indent=2))
    
    print("\n\nValidation Error Response:")
    error_response = {
        "success": False,
        "extracted_data": {
            "vendor_name": "ABC Corporation",
            "invoice_number": None,
            "invoice_date": "2024-01-15",
            "subtotal": 3000.0,
            "tax": 250.0,
            "total_amount": 3255.0,
            "currency": "USD"
        },
        "validation": {
            "is_valid": False,
            "errors": [
                {
                    "field": "invoice_number",
                    "message": "Invoice number is missing but required for processing",
                    "severity": "error"
                },
                {
                    "field": "total_amount",
                    "message": "Math error: Subtotal (3000.00) + Tax (250.00) = 3250.00, but Total is 3255.00. Difference: 5.00",
                    "severity": "error"
                }
            ],
            "warnings": []
        },
        "processing_notes": "Found 2 validation errors"
    }
    print(json.dumps(error_response, indent=2))


if __name__ == "__main__":
    print("=" * 60)
    print("AI Invoice Processing API - Usage Examples")
    print("=" * 60)
    print("\nMake sure the API is running:")
    print("  uvicorn app.main:app --reload")
    print("\n" + "=" * 60)
    
    # Run examples
    try:
        example_root_endpoint()
        example_health_check()
        example_upload_with_requests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("Make sure the API is running:")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    # Always show these examples
    example_with_curl()
    example_expected_responses()
    
    print("\n" + "=" * 60)
    print("For interactive testing, visit: http://127.0.0.1:8000/docs")
    print("=" * 60)
