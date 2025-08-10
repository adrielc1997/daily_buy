import time
import requests
import hmac
import base64
import json
import os
import datetime

BASE_URL = "https://my.okx.com"  # Ensure this is the correct API URL

# --- Environment Variables for Crypto Asset Privacy ---
# These will be read from your .env file locally and GitHub Secrets in production
API_KEY = os.getenv("OKX_API_KEY")
SECRET_KEY = os.getenv("OKX_SECRET_KEY")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")
# The actual cryptocurrency symbol (e.g., "BTC", "ETH")
CCY_CRYPTO_ASSET = os.getenv("OKX_CCY_CRYPTO_ASSET")
# The instrument ID for trading the crypto asset against USDT (e.g., "BTC-USDT", "ETH-USDT")
INST_ID_CRYPTO_USDT = os.getenv("OKX_INST_ID_CRYPTO_USDT")


def get_okx_server_time():
    """Fetch OKX server time in ISO 8601 format with milliseconds."""
    url = BASE_URL + "/api/v5/public/time"
    try:
        response = requests.get(url)
        response.raise_for_status()
        ts = response.json()['data'][0]['ts']
        dt = datetime.datetime.utcfromtimestamp(int(ts) / 1000)
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    except Exception as e:
        raise Exception(f"Failed to get OKX server time: {e}")

def get_okx_headers(method, request_path, body=''):
    """Create signed headers required for OKX API requests."""
    timestamp = get_okx_server_time()
    prehash = f"{timestamp}{method}{request_path}{body}"
    sign = hmac.new(SECRET_KEY.encode(), prehash.encode(), digestmod='sha256').digest()
    sign_b64 = base64.b64encode(sign).decode()
    return {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': sign_b64,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }

def place_order(instId, side, ccy, sz):
    """Place a market order on OKX."""
    endpoint = "/api/v5/trade/order"
    url = BASE_URL + endpoint
    order = {
        "instId": instId,
        "tdMode": "cash",
        "side": side,
        "ordType": "market",
        "ccy": ccy,
        "sz": sz
    }
    body_str = json.dumps(order)
    headers = get_okx_headers("POST", endpoint, body_str)
    try:
        response = requests.post(url, headers=headers, data=body_str)
        return response.status_code, response.json()
    except Exception as e:
        print(f"Order placement failed: {e}")
        return None, None

# --- NEW FUNCTION ---
def get_specific_balance(ccy):
    """Fetch available balance for a specific currency."""
    endpoint = "/api/v5/account/balance"
    url = BASE_URL + endpoint
    headers = get_okx_headers("GET", endpoint, "")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json().get("code") == "0":
            data = response.json()["data"]
            for asset_group in data:
                details = asset_group.get("details", [])
                for asset in details:
                    if asset.get("ccy") == ccy:
                        return float(asset.get("availBal", "0"))
            return 0.0
        else:
            print("Failed to fetch balances:", response.text)
            return 0.0
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return 0.0

# --- NEW FUNCTION ---
def get_trade_details_by_order_id(ord_id):
    """Fetch trade details by order ID to get the filled amount."""
    endpoint = "/api/v5/trade/fills"
    url = f"{BASE_URL}{endpoint}?ordId={ord_id}"
    headers = get_okx_headers("GET", f"{endpoint}?ordId={ord_id}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json().get("code") == "0":
            data = response.json().get("data", [])
            if data:
                trade_fill = data[0]
                return {
                    "sz": trade_fill.get("sz", "0"),
                    "px": trade_fill.get("px", "0"),
                    "fee": trade_fill.get("fee", "0"),
                    "feeCcy": trade_fill.get("feeCcy", "")
                }
        return {"sz": "0", "px": "0", "fee": "0", "feeCcy": ""}
    except Exception as e:
        print(f"Error fetching trade details: {e}")
        return {"sz": "0", "px": "0", "fee": "0", "feeCcy": ""}

def buy_usdt_with_sgd(amount_sgd):
    """Buy USDT using SGD via market order."""
    print(f"Buying USDT with SGD amount: {amount_sgd}")
    status, resp = place_order("USDT-SGD", "buy", "SGD", amount_sgd)
    print(f"USDT Buy Status: {status}")
    print(f"USDT Buy Response: {resp}")
    if status == 200 and resp and resp.get("code") == "0":
        return True, resp['data'][0]['ordId']
    else:
        print("Failed to place USDT buy order.")
        return False, None

def buy_crypto_with_usdt(amount_usdt):
    """Buy a crypto asset using USDT via market order."""
    if amount_usdt <= 0:
        print(f"No USDT available to buy {CCY_CRYPTO_ASSET}")
        return False, None
    amount_str = str(round(amount_usdt, 6))
    print(f"Buying {CCY_CRYPTO_ASSET} with USDT amount: {amount_str}")
    status, resp = place_order(INST_ID_CRYPTO_USDT, "buy", "USDT", amount_str)
    print(f"{CCY_CRYPTO_ASSET} Buy Status: {status}")
    print(f"{CCY_CRYPTO_ASSET} Buy Response: {resp}")
    if status == 200 and resp and resp.get("code") == "0":
        return True, resp['data'][0]['ordId']
    else:
        print(f"Failed to place {CCY_CRYPTO_ASSET} buy order.")
        return False, None

if __name__ == "__main__":
    # --- UPDATED LOGGING LOGIC ---
    now_sgt = datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=8)))
    print(f"\n--- Starting Recurring Buy at SGT: {now_sgt.strftime('%Y-%m-%d %H:%M:%S')} ---")

    # Get initial SGD balance for logging
    initial_sgd_balance = get_specific_balance("SGD")
    print(f"Initial SGD balance: {initial_sgd_balance:.2f}")

    buy_amount = os.getenv("OKX_BUY_AMOUNT_SGD", "5")
    success_usdt, usdt_order_id = buy_usdt_with_sgd(buy_amount)

    if success_usdt:
        print("USDT buy order placed successfully.")
        
        # Get final SGD balance for logging
        final_sgd_balance = get_specific_balance("SGD")
        print(f"Final SGD balance: {final_sgd_balance:.2f}")
        
        time.sleep(5) 
        
        # Get initial Crypto Asset balance for logging
        initial_crypto_asset_balance = get_specific_balance(CCY_CRYPTO_ASSET)
        
        usdt_balance = get_specific_balance("USDT")
        print(f"Available USDT balance: {usdt_balance}")
        
        success_crypto, crypto_order_id = buy_crypto_with_usdt(usdt_balance)
        
        if success_crypto:
            print("Crypto buy order placed successfully.")
            
            # --- GET FILLED AMOUNT ---
            time.sleep(5) # Allow time for trade to settle
            trade_fill_details = get_trade_details_by_order_id(crypto_order_id)
            
            # Extract the necessary values from the trade fill details
            trade_amount = trade_fill_details.get("sz")
            trade_price = trade_fill_details.get("px")
            fee_cost = trade_fill_details.get("fee")
            fee_currency = trade_fill_details.get("feeCcy")
            total_usd_cost = usdt_balance # This is the available USDT used for the trade
            
            # --- Prepare and save the requested trade data to a file ---
            trade_data = {
                "timestamp": now_sgt.strftime('%Y-%m-%d %H:%M:%S'),
                "trading_pair": INST_ID_CRYPTO_USDT,
                "side": "BUY",
                "trade_price": trade_price,
                "trade_amount": trade_amount,
                "total_usd_cost": total_usd_cost,
                "fee_cost": fee_cost,
                "fee_currency": fee_currency
            }
            with open("trade_log.json", "w") as f:
                json.dump(trade_data, f, indent=4)
            print("Trade data saved to trade_log.json")
        else:
            print(f"Aborting {CCY_CRYPTO_ASSET} buy since USDT buy failed. Fix needed.")
    else:
        print(f"Aborting {CCY_CRYPTO_ASSET} buy since USDT buy failed. Fix needed.")
