import requests
import time
import hashlib
import hmac
import base64

# Replace these with your actual API credentials
api_key = "bg_c7ad5aa555654f3a23d7ff8caabe2667"
api_secret = "6e2f5fd92f7c9bb7f5ba7fca7f63dae97d7284c44619b0e165ef405769a5d2e5"
passphrase = "rostae01"

# Prepare the request parameters
url = "https://api.bitget.com/api/v2/mix/order/cancel-order"
timestamp = str(int(time.time() * 1000))  # Current timestamp in milliseconds

# Create the request payload
data = {
    "orderId": "1232976766033367042",
    "symbol": "BTCUSDT",
    "productType": "usdt-futures",
    "marginCoin": "USDT"
}

# Convert the body to JSON format
body = str(data).replace("'", '"')  # Ensure proper JSON format

# Create the request path
request_path = "/api/v2/mix/order/cancel-order"

# Generate the signature content
signature_content = f"{timestamp}POST{request_path}{body}"

# Step 1: Generate HMAC SHA256 signature
signature = hmac.new(api_secret.encode('utf-8'), signature_content.encode('utf-8'), hashlib.sha256).digest()

# Step 2: Base64 encode the HMAC result
access_sign = base64.b64encode(signature).decode('utf-8')

# Create the headers
headers = {
    "ACCESS-KEY": api_key,
    "ACCESS-SIGN": access_sign,
    "ACCESS-PASSPHRASE": passphrase,
    "ACCESS-TIMESTAMP": timestamp,
    "locale": "zh-CN",
    "Content-Type": "application/json"
}

# Send the POST request
response = requests.post(url, headers=headers, json=data)

# Print the response
print(response.status_code)
print(response.json())
