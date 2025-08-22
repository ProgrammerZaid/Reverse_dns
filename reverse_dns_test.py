import dns.resolver
import socket
from threading import Thread, Lock

domains = {}
lock = Lock()

resolver = dns.resolver.Resolver()
resolver.nameservers = ["8.8.8.8"]
resolver.port = 53

def reverse_ip(ip):
    try:
        result = socket.gethostbyaddr(ip)
        return result[0]
    except:
        return None

def dns_request(domain):
    try:
        answers = resolver.resolve(domain)
    except:
        return
    address_list = [a.to_text() for a in answers]
    
    with lock:
        if domain not in domains:
            domains[domain] = address_list
        else:
            domains[domain] = list(set(domains[domain] + address_list))

    threads = []
    for ip in address_list:
        rev = reverse_ip(ip)
        if rev:
            with lock:
                if rev not in domains:
                    t = Thread(target=dns_request, args=(rev,))
                    t.start()
                    threads.append(t)
    for t in threads:
        t.join()

def hosty(subdomains_list, target_domain):
    threads = []
    for sub in subdomains_list:
        for prefix in ["", "www."]:
            full_domain = prefix + sub + "." + target_domain
            t = Thread(target=dns_request, args=(full_domain,))
            t.start()
            threads.append(t)
    for t in threads:
        t.join()

    for k, v in domains.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    target = input("Enter target domain (e.g., example.com): ").strip()
    with open("readme.txt", "r") as f:
        subdomains = f.read().splitlines()
    hosty(subdomains, target)
