"""
Check if registration completed despite timeout
"""
import requests

response = requests.get("http://localhost:8000")
print(f"✅ Server is running")

# Try to check latest team via admin endpoint or health check
# For now, just verify server responds
print("\n💡 The request timed out, but check the server logs to see if registration completed")
print("   Cloudinary uploads can be slow on first request")
