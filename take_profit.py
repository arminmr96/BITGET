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
    take_profit_levels = [0.1, 0.2, 0.3, 0.35]  # Profit levels
    take_profit_percents = [0.1, 0.2, 0.3, 0.4]  # Profit percentages
    take_profit_flags = [False for i in range(4)]

    while True:
        # Get the latest price
        current_price = get_price(symbol).json()["data"][0]["lastPr"]
        if current_price is None:
            continue
        
        # Check take profit levels
        for i in range(len(take_profit_levels)):
            take_profit_level = take_profit_levels[i]
            take_profit_percent = take_profit_percents[i]
            take_profit_price = initial_price * (1 + take_profit_level)
            if current_price >= take_profit_price and take_profit_flags[i] == False:
                current_size = take_profit_percent * size
                # Place a take profit order
                place_order(symbol, "sell", current_size, current_price)
                take_profit_flags[i] = True
                print(f"Take profit order placed at {take_profit_price}.")
                break
        
        if all(take_profit_flags):
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
    


