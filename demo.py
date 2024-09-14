from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Define the API keys and endpoints
IP_GEOLOCATION_API_KEY = 'your_ip_geolocation_api_key'
WHOIS_XML_API_KEY = 'your_whois_xml_api_key'

def get_domain_info(domain):
    response = requests.get(f'https://api.ipgeolocation.io/ipgeo?apiKey={IP_GEOLOCATION_API_KEY}&ip={domain}')
    data = response.json()
    return {
        "ip": data.get("ip"),
        "isp": data.get("isp"),
        "organization": data.get("organization"),
        "asn": data.get("asn"),
        "location": data.get("country_name")
    }

def get_subdomains(domain):
    response = requests.get(f'https://subdomains.whoisxmlapi.com/api/v1?apiKey={WHOIS_XML_API_KEY}&domainName={domain}')
    data = response.json()
    return data.get("subdomains", [])

def extract_assets(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    assets = {
        "javascripts": [],
        "stylesheets": [],
        "images": [],
        "iframes": [],
        "anchors": []
    }
    
    for script in soup.find_all('script', src=True):
        assets['javascripts'].append(script['src'])
    
    for link in soup.find_all('link', rel='stylesheet'):
        assets['stylesheets'].append(link['href'])
    
    for img in soup.find_all('img', src=True):
        assets['images'].append(img['src'])
    
    for iframe in soup.find_all('iframe', src=True):
        assets['iframes'].append(iframe['src'])
    
    for anchor in soup.find_all('a', href=True):
        assets['anchors'].append(anchor['href'])
    
    return assets

@app.route('/', methods=['GET'])
def analyze_website():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    domain_info = get_domain_info(url)
    subdomains = get_subdomains(url)
    asset_domains = extract_assets(url)
    
    result = {
        "info": domain_info,
        "subdomains": subdomains,
        "asset_domains": asset_domains
    }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
