import csv
import time
import string
from typing import Dict

from bs4 import BeautifulSoup
from playwright.sync_api import Playwright, sync_playwright, expect


ALPHABETS = string.ascii_uppercase
DIGITS = string.digits
FILENAME = 'hopkins-properties.csv'

SEARCH_VARIABLES = ALPHABETS + DIGITS


def extract_property_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        owner = soup.select_one('td#webprop_name').getText(separator=', ', strip=True)
    except Exception as e:
        print(e)
        owner = ''
    try:
        owner_address = soup.select_one('td#webprop_mailaddress').getText(separator=', ', strip=True)
    except Exception as e:
        print(e)
        owner_address = ''
    try:
        legal = soup.select_one('td#webprop_desc').getText(separator=', ', strip=True)
    except Exception as e:
        print(e)
        legal = ''
    try:
        situs = soup.select_one('td#webprop_situs').getText(separator=', ', strip=True)
    except Exception as e:
        print(e)
        situs = ''
    try:
        improvements = soup.select_one('td#histimp0_yr').getText(separator=', ', strip=True)
    except Exception as e:
        improvements = ''
    try:
        lmv = soup.select_one('td#histlnd0_yr').getText(separator=', ', strip=True)
    except Exception as e:
        lmv = ''
    try:
        tmv = soup.select_one('td#histmkt0_yr').getText(separator=', ', strip=True)
    except Exception as e:
        tmv = ''
    try:
        tav = soup.select_one('td#histassd0_yr').getText(separator=', ', strip=True)
    except Exception as e:
        tav = ''
    try:
        land_code = soup.select_one('tbody#tableLnd tr td').getText(separator=', ', strip=True)
    except Exception as e:
        land_code = ''
    try:
        acres = soup.select_one('tbody#tableLnd tr td:nth-of-type(2)').getText(separator=', ', strip=True)
    except Exception as e:
        acres = ''
    try:
        ldd = soup.select_one('tbody#tableSale tr td:nth-of-type(4)').getText(separator=', ', strip=True)
    except Exception as e:
        ldd = ''
    try:
        sold_by = soup.select_one('tbody#tableSale tr td:nth-of-type(1)').getText(separator=', ', strip=True)
    except Exception as e:
        sold_by = ''
    try:
        ldp = soup.select_one('tbody#tableSale tr td:nth-of-type(3)').getText(separator=', ', strip=True)
    except Exception as e:
        ldp = ''
    try:
        ldv = soup.select_one('tbody#tableSale tr td:nth-of-type(2)').getText(separator=', ', strip=True)
    except Exception as e:
        ldv = ''
    try:
        ldi = soup.select_one('tbody#tableSale tr td:nth-of-type(5)').getText(separator=', ', strip=True)
    except Exception as e:
        ldi = ''

    return {
        'Property ID': soup.select_one('td#ucidentification_webprop_id').getText(separator=', ', strip=True),
        'Geo ID': soup.select_one('td#ucidentification_webprop_geoid').getText(separator=', ', strip=True),
        'Owner Name': owner,
        'Mailing Address': owner_address,
        'Legal Description': legal,
        'Situs': situs,
        'Improvements': improvements,
        'Land Market Value': lmv,
        'Total Market Value': tmv,
        'Total Assessed Value': tav,
        'Land Code': land_code,
        'Total Acres': acres,
        'Last Deed Date': ldd,
        'Sold By': sold_by,
        'Deed Pages': ldp,
        'Deed Volumn': ldv,
        'Deed Instruments': ldi
    }


def populate_csvfile(data: Dict, filename: str, add_headers=False):
    fieldnames = [item for item in data.keys()]
    row_values = [item for item in data.values()]
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        if add_headers:
            # Write the header row with fieldnames
            writer.writerow(fieldnames)
        # Write row values
        writer.writerow(row_values)


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    add_headers = True
    for char in SEARCH_VARIABLES[9:]:
        print(f'SEARCH STRING = {char}')
        page.goto("https://iswdataclient.azurewebsites.net/webindex.aspx?dbkey=HOPKINSCAD")
        # time.sleep(20)
        page.locator('#searchHeaderX_searchname').fill(char)
        page.get_by_role("button", name="Search", exact=True).click()
        page.wait_for_load_state('networkidle')
        all_properties = page.query_selector_all('div#dvPrimary tbody tr')
        n = len(all_properties)
        try:
            n = int(n) - 1
        except Exception as e:
            print(f'Failed to get total for {char} - {e}')
            continue
        page.query_selector('a[id^="ucResultsGrid"]').click()
        page.wait_for_load_state('networkidle')
        for i in range(n):
            # page.get_by_role('button', name='Next', exact=False).click()
            page.wait_for_selector('//th[text() = "Acres"]')
            content = extract_property_info(page.content())
            print(content)
            page.query_selector('a#ucidentification_lbNext').click(timeout=100*1000)
            populate_csvfile(content, FILENAME, add_headers)
            add_headers = False
        # break

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
