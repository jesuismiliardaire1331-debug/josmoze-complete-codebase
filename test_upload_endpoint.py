#!/usr/bin/env python3
"""
Test script for the new upload-product-image endpoint
"""
import requests
import io
from PIL import Image

def test_upload_endpoint():
    """Test the upload-product-image endpoint"""
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # Prepare the form data
    files = {
        'image': ('test_image.jpg', img_bytes, 'image/jpeg')
    }
    
    data = {
        'product_id': 'test-product-123',
        'replace_current': 'true'
    }
    
    try:
        # Make the request
        response = requests.post(
            'http://localhost:8000/api/admin/upload-product-image',
            files=files,
            data=data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Endpoint is working correctly!")
            return True
        else:
            print("❌ Endpoint returned an error")
            return False
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

if __name__ == "__main__":
    test_upload_endpoint()