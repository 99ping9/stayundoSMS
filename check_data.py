import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.database import get_supabase

sb = get_supabase()

t = sb.table('v3_message_templates').select('accommodation_name,trigger_type,is_active').order('accommodation_name,trigger_type').execute()
print(f'Total templates: {len(t.data)}')
for x in t.data:
    acc = x['accommodation_name']
    trig = x['trigger_type']
    active = x['is_active']
    print(f'  {acc:12} | {trig:25} | active={active}')

r = sb.table('v3_reservations').select('accommodation_name,guest_name,checkin_date,checkout_date').execute()
print(f'\nTotal reservations: {len(r.data)}')
for x in r.data[:10]:
    print(f'  {x["accommodation_name"]} | {x["guest_name"]} | {x["checkin_date"]}~{x["checkout_date"]}')
