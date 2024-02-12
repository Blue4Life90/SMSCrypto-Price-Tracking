import os
import smtplib
import getpass
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

base_url = 'https://pro-api.coinmarketcap.com'
endpoint = '/v1/cryptocurrency/listings/latest'
url = base_url + endpoint

headers = {
    'X-CMC_PRO_API_KEY': os.environ.get('API_KEY')
}

session = Session()
session.headers.update(headers)

threshold_percent = 5 # set the threshold percentage here

try:
    response = session.get(url, headers=headers)
    data = response.json()
    if 'data' in data:
        bitcoin_data = next((currency for currency in data['data'] if currency['symbol'] == 'BTC'), None)
        eth_data = next((currency for currency in data['data'] if currency['symbol'] == 'ETH'), None)
        if bitcoin_data and eth_data:
            bitcoin_price = bitcoin_data['quote']['USD']['price']
            eth_price = eth_data['quote']['USD']['price']
            # % of change in 24hr var
            BTC_percent_change_24h = bitcoin_data['quote']['USD']['percent_change_24h']
            ETH_percent_change_24h = eth_data['quote']['USD']['percent_change_24h']
            if abs(BTC_percent_change_24h) >= threshold_percent:
                message = f'Heads up! Bitcoin just had a {BTC_percent_change_24h} change!\n\nCurrent prices below.\n\nBitcoin price: ${round(bitcoin_price, 2)}\nEthereum price: ${round(eth_price, 2)}'
            elif abs(ETH_percent_change_24h) >= threshold_percent:
                message = f'Heads up! Ethereum just had a {ETH_percent_change_24h} change!\n\nCurrent prices below.\n\nBitcoin price: ${round(bitcoin_price, 2)}\nEthereum price: ${round(eth_price, 2)}'
            else:
                message = f"BTC/ETH prices within the threshold.\nCurrent prices below.\n\nBitcoin price: ${round(bitcoin_price, 2)}\nEthereum price: ${round(eth_price, 2)}"
        else:
            message = 'Bitcoin and/or Ethereum data not found in the response'
    else:
        message = "No 'data' field found in the response."
except (ConnectionError, Timeout, TooManyRedirects) as e:
    message = e    

s_server = 'smtp.gmail.com'
port = 587

email_address = os.environ.get('email_address')
mail_password = os.environ.get('mail_password')
sender_number = os.environ.get('sender_number')
recipient_number = os.environ.get('recipient_number')

# New Line prevents the CMAE (Cloudmark Authority Engine) banner in the message when using php mail services
message_content = "\n" + message
sender_message = f'This is a test message from {sender_number}\nTo: {recipient_number}\nSubject: SMS Test\n\n{message_content}'

try:
    with smtplib.SMTP(s_server, port) as server:
        server.starttls()
        server.login(email_address, mail_password)
        server.sendmail(sender_number, recipient_number, message_content)
except Exception as e:
    print(f'Error sending mail: {e}')
