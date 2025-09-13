import subprocess
import sys
import requests
import datetime
import os

os.system("")

class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

TEBEX_SECRET_KEY = "PASTEYOURTEBEXGAMESERVERSECREKEYHERE"

def get_all_payments(api_key):
    headers = {'X-Tebex-Secret': api_key}
    all_payments = []
    page = 1
    
    print(f"{C.CYAN}Getting data from Tebex...{C.ENDC}")
    
    while True:
        params = {'page': page}
        try:
            response = requests.get("https://plugin.tebex.io/payments", headers=headers, params=params, timeout=15)
            response.raise_for_status()
            
            response_data = response.json()
            payments_on_page = []

            if isinstance(response_data, dict):
                payments_on_page = response_data.get('data', [])
            elif isinstance(response_data, list):
                payments_on_page = response_data
                all_payments.extend(payments_on_page)
                break 
            
            if not payments_on_page:
                break
            
            all_payments.extend(payments_on_page)
            print(f"{C.CYAN}Fetched page {page}...{C.ENDC}")
            page += 1
            
        except requests.exceptions.HTTPError as e:
            print(f"\n{C.RED}{C.BOLD}HTTP Error: {e.response.status_code} | Please check your TEBEX_SECRET_KEY (29 line){C.ENDC}")
            return None

    print(f"\n{C.GREEN}Successfully fetched {len(all_payments)} payments{C.ENDC}")
    return all_payments

def main():
    try:
        year_input = input(f"{C.YELLOW}Enter the year (e.g., 2025): {C.ENDC}")
        month_input = input(f"{C.YELLOW}Enter the month (1-12): {C.ENDC}")
        year = int(year_input)
        month = int(month_input)
        if not (1 <= month <= 12):
            print(f"{C.RED}Enter correct month{C.ENDC}")
            return
    except ValueError:
        print(f"{C.RED}Stop trolling{C.ENDC}")
        return

    payments = get_all_payments(TEBEX_SECRET_KEY)
    
    if payments is None:
        return

    total_sum = 0.0
    payment_count = 0
    currency = ""
    product_sales = {}

    for payment in payments:
        payment_date = datetime.datetime.fromisoformat(payment['date'].replace('Z', '+00:00'))
        
        if payment_date.year == year and payment_date.month == month:
            amount = float(payment['amount'])
            total_sum += amount
            payment_count += 1
            
            if not currency:
                currency = payment['currency']['iso_4217']

            packages = payment.get('packages')
            if packages:
                package_names = [pkg['name'] for pkg in packages]
                product_name = ", ".join(package_names)
                
                current_product_total = product_sales.get(product_name, 0.0)
                product_sales[product_name] = current_product_total + amount
            else:
                product_name = "(No Package Specified)"
                current_product_total = product_sales.get(product_name, 0.0)
                product_sales[product_name] = current_product_total + amount

    print(f"\n{C.BOLD}{C.BLUE}--- Summary ---{C.ENDC}")
    print(f"{C.BOLD}Selected period: {month:02d}-{year}{C.ENDC}")

    if payment_count > 0:
        print(f"Found {payment_count} payments in this period")
        print(f"{C.BOLD}Total income: {C.GREEN}{total_sum:.2f} {currency}{C.ENDC}")

        if product_sales:
            print(f"\n{C.BOLD}{C.BLUE}--- Product Breakdown (sorted by revenue) ---{C.ENDC}")
            sorted_products = sorted(product_sales.items(), key=lambda item: item[1], reverse=True)
            
            for name, total in sorted_products:
                print(f"- {C.YELLOW}{name}{C.ENDC}: {C.GREEN}{total:.2f} {currency}{C.ENDC}")
    else:
        print(f"{C.YELLOW}No payments found for the selected period{C.ENDC}")

if __name__ == "__main__":
    main()