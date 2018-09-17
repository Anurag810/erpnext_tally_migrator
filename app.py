import logging
import sys
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup as bs
import requests
from queries import account_query, company_query, group_account_query

TALLY_HOST = sys.argv[1]
TALLY_PORT = sys.argv[2] if len(sys.argv) == 3 else 9000
TALLY_PATH = "http://{}:{}".format(TALLY_HOST, TALLY_PORT)

logging.basicConfig(level=logging.INFO)

def main():
    logging.info("Connecting to Tally Server on {}".format(TALLY_PATH))
    try:
        response = requests.get(TALLY_PATH, timeout=1)
        if response.status_code == 200:
            logging.info("Connected")
            companies = get_companies()
            if companies:
                logging.info("Companies Found : {}".format(companies))
                # Hardcoding for now
                # Should be chosen from UI
                company = companies[1]
                logging.info("Choosing company : {}".format(company))

                # Hardcoding connection details for now
                session = connect_to_erpnext("http://erpnext.local:8000", "Administrator", "admin")
            else:
                logging.warning("No Companies Found")
    except:
        import traceback
        traceback.print_exc()
        logging.warning("Connection Failed")

def get_companies():
    response = requests.post(TALLY_PATH, data=company_query)
    response = bs(response.text, "xml")
    collection = response.ENVELOPE.BODY.DATA.COLLECTION
    companies = collection.find_all("COMPANY")
    company_list = []
    for company in companies:
        company_list.append(company.NAME.string)
    return company_list

def get_accounts(company):
    response = requests.post(TALLY_PATH, data=account_query.format(company))
    response = bs(response.text, "xml")
    collection = response.ENVELOPE.BODY.DATA.COLLECTION
    accounts = collection.find_all("LEDGER")
    account_list = []
    for account in accounts:
        account_list.append(account.NAME.string)
    return account_list

def get_group_accounts(company):
    response = requests.post(TALLY_PATH, data=group_account_query.format(company))
    response = bs(response.text, "xml")
    collection = response.ENVELOPE.BODY.DATA.COLLECTION
    accounts = collection.find_all("GROUP")
    account_list = []
    for account in accounts:
        account_list.append(account.NAME.string)
    return account_list

def connect_to_erpnext(server_path, username, password):
    session = requests.Session()
    response = session.post(server_path,
        data={
            'cmd': 'login',
            'usr': username,
            'pwd': password
        }
    )
    if response.status_code == 200:
        data = response.json()
        logging.info("Logged in as {}".format(data["full_name"]))
        return session
    else:
        logging.warning("Login failed")

main()
