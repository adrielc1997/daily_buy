# Recurring Crypto Spot Buy Bot 🤖

This repository contains a Python script designed to automate recurring spot purchases of a chosen cryptocurrency on the OKX exchange. It's set up to run automatically using GitHub Actions, leveraging environment variables for secure credential management and privacy.

---

## 🌟 Features

* **Automated Trading:** Executes recurring market buy orders on OKX.
* **Secure Credential Handling:** Utilizes GitHub Secrets to securely store API keys, secret keys, and passphrases, keeping them out of the public codebase.
* **Privacy-Focused:** The specific cryptocurrency being traded is configured via private environment variables, ensuring it's not hardcoded in the public repository.
* **Flexible Scheduling:** Configured to run on a schedule using GitHub Actions' `cron` jobs.
* **Balance Logging:** Tracks and logs balance changes for SGD and the purchased crypto asset.

---

## 🚀 Setup & Configuration

To get this bot up and running, you'll need to configure your OKX API credentials and define the trading parameters using GitHub Secrets.

### 1. GitHub Repository

* Ensure your repository is set up on GitHub.
* This repository's history should be clean of any sensitive information.

### 2. OKX API Keys

* Create an API Key on your OKX account with **Trade** and **Read** permissions.
* Ensure you have your **API Key**, **Secret Key**, and **Passphrase**.

### 3. GitHub Secrets

Navigate to your GitHub repository's **`Settings`** > **`Secrets and variables`** > **`Actions`**. Add the following repository secrets:

* `OKX_API_KEY`: Your OKX API Key.
* `OKX_SECRET_KEY`: Your OKX Secret Key.
* `OKX_PASSPHRASE`: Your OKX Passphrase.
* `OKX_BUY_AMOUNT_SGD`: The amount in SGD you wish to spend on each recurring buy (e.g., `5`).
* `OKX_CCY_CRYPTO_ASSET`: The symbol of the crypto asset you want to buy (e.g., `BTC`, `ETH`).
* `OKX_INST_ID_CRYPTO_USDT`: The instrument ID for the trading pair (e.g., `BTC-USDT`, `ETH-USDT`).

**Important:** Do not include quotes when entering the secret values.

### 4. Self-Hosted Runner (Optional, but recommended for static IP)

The workflow is configured to run on a `self-hosted` runner with the `okx-static-ip` label. This is crucial if OKX requires API calls from a static IP address. If you're not using a self-hosted runner or don't need a static IP, you'll need to adjust the `runs-on` line in `.github/workflows/recurring-buy.yml`.

---

## ⚙️ How It Works

The bot operates through a GitHub Actions workflow (`.github/workflows/recurring-buy.yml`):

1.  **Schedule:** The `cron` schedule (`0 0 * * *`) means the bot will attempt to run daily at 00:00 UTC. You can modify this cron expression to suit your desired frequency.
2.  **Checkout Code:** It checks out your repository code.
3.  **Virtual Environment:** Sets up a Python virtual environment to manage dependencies.
4.  **Install Dependencies:** Installs necessary Python libraries (e.g., `requests`).
5.  **Run Script:** Executes the `buy.py` script, which reads the configured environment variables (from GitHub Secrets) and interacts with the OKX API to place orders.

---

## ⚠️ Disclaimer

This bot is provided for educational and informational purposes only. Trading cryptocurrencies involves substantial risk of loss and is not suitable for every investor. You should carefully consider your investment objectives, level of experience, and risk appetite before engaging in any trading activity. The author is not responsible for any financial losses incurred from using this bot. Always do your own research and understand the risks involved.
