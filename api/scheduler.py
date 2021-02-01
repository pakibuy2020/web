from apscheduler.schedulers.background import BackgroundScheduler
from cart.models import *

import requests

# this checks every minute for payment in progress status 
# since paymongo dosen't provide an api to check for cancel/failed
# only cheargeable
def process_inprogress_payments():
    payments = Payment.objects.filter(payment_status=2)
    for payment in payments:
        if payment.payment_type == 1:
            paymongo_id = payment.paymongo_id
            url = "https://api.paymongo.com/v1/sources/" + paymongo_id

            headers = { "Content-Type": "application/json",
                        "Authorization": "Basic c2tfdGVzdF9ZcGJCNXZheVE2dWsyZHFZUzl2VkdoRHg6c2tfdGVzdF9ZcGJCNXZheVE2dWsyZHFZUzl2VkdoRHg="
                    }

            response = requests.request("GET", url, headers=headers)
            
            if response.status_code == 200:
                json_data = response.json()
                status = json_data['data']['attributes']['status']
                print('status of ' + paymongo_id + ' is ' + status)

        
                if status == 'cancelled' or status == 'expired':
                    status = 4 if status == 'cancelled' else 3
                    Payment.objects.filter(paymongo_id=paymongo_id).update(payment_status=status)
                    # update cart status to rejected
                    payment = Payment.objects.get(paymongo_id=paymongo_id)
                    Cart.objects.filter(id=payment.cart.id).update(status=5)
                else:
                    # if the customer authorized the payment
                    if status == 'chargeable':
                        # then make the actual payment since the status is chargeable
                        process_actual_payment(paymongo_id=paymongo_id,headers=headers)

# process the actual payment from gcash
# call the paymongo api to deduct money from customer's gcash account
# if successfull change the cart status to shipping
def process_actual_payment(paymongo_id,headers):
    source_url = "https://api.paymongo.com/v1/sources/" + paymongo_id
    response_source = requests.request("GET", source_url, headers=headers)
    if response_source.status_code == 200:
        source_json_data = response_source.json()
        amount_source = source_json_data['data']['attributes']['amount']
        payment_url = "https://api.paymongo.com/v1/payments"
        payload = {
            'data': {
                'attributes': {
                    'amount': amount_source,
                    'source': {
                        'id': paymongo_id,
                        'type': 'source'
                    },
                    'currency': 'PHP'
                }
            }
        }
        response_payment = requests.request("POST", payment_url, json=payload, headers=headers)
        if response_payment.status_code == 200:
            print('paid successfully')
            # update status
            try:
                Payment.objects.filter(paymongo_id=paymongo_id).update(payment_status=1)
                payment = Payment.objects.get(paymongo_id=paymongo_id)
                cart_id = payment.cart.id
                Cart.objects.filter(id=cart_id).update(status=3)
            except Payment.DoesNotExist:
                pass

def start():
    scheduler = BackgroundScheduler()

    # check in progress payments
    scheduler.add_job(process_inprogress_payments, 'interval', seconds=60)

    scheduler.start()