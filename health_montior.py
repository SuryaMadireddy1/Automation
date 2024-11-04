import yaml
import requests
import time
from urllib.parse import urlparse

def load_config(file_path):
    try:
        with open(file_path, 'r') as file:  # Load endpoints from YAML file
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        sys.exit(1)

def check_endpoint(endpoint):
    try:
        url = endpoint['url']
        method = endpoint.get('method', 'GET')
        headers = endpoint.get('headers', {})
        body = endpoint.get('body', None)
        
        start_time = time.time()
        response = requests.request(method, url, headers=headers, data=body, timeout=0.5)
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds

        return (200 <= response.status_code < 300) and (latency < 500)
    except requests.RequestException:
        return False

def monitor_endpoints(config_file):
    endpoints = load_config(config_file)
    stats = {}

    try:
        while True:
            for endpoint in endpoints:
                domain = urlparse(endpoint['url']).netloc
                if domain not in stats:
                    stats[domain] = {'up': 0, 'total': 0}
                
                is_up = check_endpoint(endpoint)
                stats[domain]['total'] += 1
                if is_up:
                    stats[domain]['up'] += 1
                
            for domain, domain_stats in stats.items():
                availability = round(100 * domain_stats['up'] / domain_stats['total'])
                print(f"{domain} has {availability}% availability percentage")
            
            time.sleep(15)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py config.yaml")
        sys.exit(1)
        
    monitor_endpoints(sys.argv[1])