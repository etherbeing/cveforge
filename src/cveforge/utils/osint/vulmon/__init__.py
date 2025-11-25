from http import HTTPMethod
import logging
from typing import Any, Literal
from requests import request
from bs4 import BeautifulSoup

from cveforge.utils.cache import tcve_cache

@tcve_cache()
def consult(query: str, scoretype: Literal["cvssv3", "cvssv2", "cvssv4", "epss", "vmscore"]="cvssv3"):
    headers: dict[str, str] = {}
    headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    headers["accept-language"] = "en-US,en;q=0.5"
    headers["cache-control"] = "no-cache"
    headers["pragma"] = "no-cache"
    headers["priority"] = "u=0, i"
    headers["referer"] = "https://vulmon.com/"
    headers["sec-ch-ua"] = '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"'
    headers["sec-ch-ua-mobile"] = "?0"
    headers["sec-ch-ua-platform"] = '"Linux"'
    headers["sec-fetch-dest"] = 'document'
    headers["sec-fetch-mode"] = 'navigate'
    headers["sec-fetch-site"] = 'same-origin'
    headers["sec-fetch-user"] = "?1"
    headers["sec-gpc"] = "1"
    headers["upgrade-insecure-requests"] = "1"
    headers["user-agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    cookies: dict[str, str] = {}
    cookies["vab2"] = "3"
    page = 0
    results: dict[str, Any] = {}
    while True:
        response = request(HTTPMethod.GET, f"https://vulmon.com/searchpage?q={query}&page={page}&scoretype={scoretype}", headers=headers, cookies=cookies, timeout=10)
        if not response.ok:
            logging.warning("Response is not ok, reason %s", response.status_code)
            break
        soup = BeautifulSoup(response.text)
        vulns = soup.select_one(".Cust-Site-content")
        if not vulns:
            break
        items_list = vulns.select_one(".ui.divided.items")
        if not items_list:
            break
        items = items_list.select(".item")
        for item in items:
            name = item.select_one(".content > .header > .header")
            if name:
                name = name.get_text()
            else:
                continue
            risk = item.select_one(".statistics > .statistic > .value")
            if risk:
                risk = risk.get_text()
            summary = item.select_one(".description > a")
            if summary:
                summary = summary.get_text()
            tags = [x.get_text() for x in item.select(".extra .jsvmvendorproduct")]
            results[name] = {
                "summary": summary,
                "risk": risk,
                "tags": tags
            }
        page += 1
        return results