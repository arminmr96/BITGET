import requests
import time
import hashlib
import hmac
import base64

def create_headers(method, request_path, query_string=None, data=None):
    # API credentials
    api_key = "bg_c7ad5aa555654f3a23d7ff8caabe2667"
    api_secret = "6e2f5fd92f7c9bb7f5ba7fca7f63dae97d7284c44619b0e165ef405769a5d2e5"
    passphrase = "rostae01"

    # Prepare the request parameters
    timestamp = str(int(time.time() * 1000))  # Current timestamp in milliseconds
    
    # Convert the body to JSON format
    body = str(data).replace("'", '"')  # Ensure proper JSON format

    # Generate the signature content
    if query_string:
        signature_content = f"{timestamp}{method.upper()}{request_path}?{query_string}{body}"
        
    else:
        signature_content = f"{timestamp}{method.upper()}{request_path}{body}"

    # Generate HMAC SHA256 signature
    signature = hmac.new(api_secret.encode('utf-8'), signature_content.encode('utf-8'), hashlib.sha256).digest()

    # Base64 encode the HMAC result
    access_sign = base64.b64encode(signature).decode('utf-8')

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": access_sign,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }

    return headers

def place_order(symbol, side, size, price):
    request_path = "/api/v2/mix/order/place-order"
    url = "https://api.bitget.com" + request_path
    data = {
        "symbol": symbol,
        "productType": "usdt-futures",
        "marginMode": "isolated",
        "marginCoin": "USDT",
        "size": size,
        "price": price,
        "side": side,
        "tradeSide": "open",
        "orderType": "limit",
        "force": "gtc",
    }
    # create Headers and send POST request
    headers = create_headers("POST", request_path, data=data)
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error placing order: {response.status_code}, {response.json()}")
        return None

def get_price(symbol):
    # request_path = "/api/v2/mix/market/symbol-price"
    request_path = "/api/v2/mix/market/ticker"
    query_string = f"productType=usdt-futures&symbol={symbol}"
    url = f"https://api.bitget.com{request_path}?{query_string}"

    # create Headers and send POST request
    headers = create_headers("GET", request_path, query_string)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"][0]["lastPr"]
    else:
        print(f"Error fetching price: {response.status_code}, {response.json()}")
        return None

def monitor(symbol, size, initial_price):
    # Define trade parameters
    stop_loss_levels = [0.2, 0.3, 0.5]  # Loss levels
    stop_loss_percents = [0.2, 0.3, 0.5]  # Loss percentages
    stop_loss_flags = [False for i in range(3)]

    while True:
        # Get the latest price
        current_price = get_price(symbol).json()["data"][0]["lastPr"]
        if current_price is None:
            continue

        # Check stop loss levels
        for i in range(len(stop_loss_levels)):
            stop_loss_level = stop_loss_levels[i]
            stop_loss_percent = stop_loss_percents[i]
            stop_loss_price = initial_price * (1 - stop_loss_level)
            if current_price <= stop_loss_price and stop_loss_flags[i] == False:
                current_size = stop_loss_percent * size 

                # Place a stop loss order
                place_order(symbol, "sell", current_size, current_price)
                stop_loss_flags[i] = True
                print(f"Stop loss order placed at {current_price}.")
                break
        
        # Check for flags
        if all(stop_loss_flags):
            break
        # Sleep for 5 seconds before the next check
        time.sleep(5)

def main():
    symbol = "BTCUSDT"
    side = "buy"
    size = 1
    price = get_price(symbol).json()["data"][0]["lastPr"]  # Get current price
    place_order(symbol, side, size, price)
    
    monitor(symbol, size, price)

if __name__ == "__main__":
    main()
    


