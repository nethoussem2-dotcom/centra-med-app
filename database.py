import requests
import json
import datetime
import traceback

SUPABASE_URL = "https://spjrkydmfttwrmbakwty.supabase.co/rest/v1"
SUPABASE_KEY = "sb_publishable_cVKprMUSRtrq8rSQTWlSzA_tv_EvU5K"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def init_db():
    pass

def init_products_if_empty():
    pass

# ==========================================
# USERS API
# ==========================================

def get_user(username, password_hash):
    try:
        url = f"{SUPABASE_URL}/users?username=eq.{username}&password_hash=eq.{password_hash}&select=*"
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        if data and len(data) > 0:
            return data[0]
        return None
    except Exception as e:
        print(f"Error get_user: {e}")
        return None

def update_user_password(username, new_password_hash):
    try:
        url = f"{SUPABASE_URL}/users?username=eq.{username}"
        payload = {"password_hash": new_password_hash}
        res = requests.patch(url, headers=HEADERS, json=payload)
        return res.status_code in (200, 204)
    except:
        return False

# ==========================================
# PRODUCTS API (art_pf)
# ==========================================

def get_active_products():
    try:
        url = f"{SUPABASE_URL}/art_pf?select=*"
        res = requests.get(url, headers=HEADERS)
        return res.json()
    except Exception as e:
        print(f"Error get_active_products: {e}")
        return []

def get_product_by_code(code_article):
    try:
        url = f"{SUPABASE_URL}/art_pf?code_article=eq.{code_article}&select=*"
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        return data[0] if data else None
    except:
        return None

def add_product(code_article, designation, poid_theo, std_dechet):
    try:
        url = f"{SUPABASE_URL}/art_pf"
        payload = {
            "code_article": code_article.strip(),
            "designation": designation.strip(),
            "poids_theorique_gr": poid_theo,
            "standard_dechet": std_dechet
        }
        res = requests.post(url, headers=HEADERS, json=payload)
        return res.status_code in (200, 201)
    except:
        return False

def update_product(code_article, designation, poid_theo, std_dechet):
    try:
        url = f"{SUPABASE_URL}/art_pf?code_article=eq.{code_article}"
        payload = {
            "designation": designation.strip(),
            "poids_theorique_gr": poid_theo,
            "standard_dechet": std_dechet
        }
        res = requests.patch(url, headers=HEADERS, json=payload)
        return res.status_code in (200, 204)
    except:
        return False

def delete_product(code_article):
    try:
        url = f"{SUPABASE_URL}/art_pf?code_article=eq.{code_article}"
        res = requests.delete(url, headers=HEADERS)
        return res.status_code in (200, 204)
    except:
        return False

# ==========================================
# PRODUCTION RECORDS API
# ==========================================

def add_production_record(date, username, code_article, designation, machine, num_lot, qte_prod, poid_theo, poid_reel, dechet_pce, dechet_kg, taux_rebut, downtime_min=0.0, downtime_reason="", colorant_kg=0.0, low_prod_reason="", high_waste_reason=""):
    try:
        url = f"{SUPABASE_URL}/production_records"
        payload = {
            "date": date,
            "username": username,
            "code_article": code_article,
            "designation": designation,
            "machine": machine,
            "num_lot": num_lot,
            "qte_prod": qte_prod,
            "poid_theo": poid_theo,
            "poid_reel": poid_reel,
            "dechet_pce": dechet_pce,
            "dechet_kg": dechet_kg,
            "taux_rebut": taux_rebut,
            "downtime_min": downtime_min,
            "downtime_reason": downtime_reason,
            "colorant_kg": colorant_kg,
            "low_prod_reason": low_prod_reason,
            "high_waste_reason": high_waste_reason
        }
        res = requests.post(url, headers=HEADERS, json=payload)
        if res.status_code in (200, 201):
            data = res.json()
            return data[0]['id'] if data else 1
        return None
    except Exception as e:
        print(f"Error add_production_record: {e}")
        return None

def get_recent_production_records(limit=1000):
    try:
        url = f"{SUPABASE_URL}/production_records?select=*&order=id.desc&limit={limit}"
        res = requests.get(url, headers=HEADERS)
        return res.json()
    except:
        return []

def get_production_records_by_date(date_str):
    try:
        url = f"{SUPABASE_URL}/production_records?date=eq.{date_str}&select=*&order=id.desc"
        res = requests.get(url, headers=HEADERS)
        return res.json()
    except:
        return []

def get_production_records_by_month(year_month):
    try:
        url = f"{SUPABASE_URL}/production_records?date=like.{year_month}-*&select=*&order=date.asc"
        res = requests.get(url, headers=HEADERS)
        return res.json()
    except:
        return []

def get_production_records_by_batch(num_lot):
    try:
        url = f"{SUPABASE_URL}/production_records?num_lot=eq.{num_lot}&select=*&order=date.asc"
        res = requests.get(url, headers=HEADERS)
        return res.json()
    except:
        return []

def update_production_record(record_id, **kwargs):
    try:
        url = f"{SUPABASE_URL}/production_records?id=eq.{record_id}"
        res = requests.patch(url, headers=HEADERS, json=kwargs)
        return res.status_code in (200, 204)
    except:
        return False

def delete_production_record(record_id):
    try:
        url = f"{SUPABASE_URL}/production_records?id=eq.{record_id}"
        res = requests.delete(url, headers=HEADERS)
        return res.status_code in (200, 204)
    except:
        return False

# ==========================================
# FEEDBACK API
# ==========================================

def add_feedback(sender_name, role, category, message):
    try:
        url = f"{SUPABASE_URL}/feedback"
        payload = {
            "sender_name": sender_name,
            "role": role,
            "category": category,
            "message": message,
            "date": datetime.datetime.now().strftime("%Y-%m-%d")
        }
        res = requests.post(url, headers=HEADERS, json=payload)
        return res.status_code in (200, 201)
    except:
        return False

def get_all_feedback():
    try:
        url = f"{SUPABASE_URL}/feedback?select=*&order=id.desc"
        res = requests.get(url, headers=HEADERS)
        return res.json()
    except:
        return []

# ==========================================
# TRANSFER RECORDS (LOG-FO-016) API
# ==========================================

def add_transfert_record(date, code_article, qte_pcs, num_lot, nb_sacs, heure_transfert, operateur, receptionnaire=""):
    try:
        url = f"{SUPABASE_URL}/transfert_records"
        payload = {
            "date": date,
            "code_article": code_article.strip(),
            "qte_pcs": qte_pcs,
            "num_lot": num_lot.strip(),
            "nb_sacs": str(nb_sacs).strip(),
            "heure_transfert": heure_transfert.strip(),
            "operateur": operateur.strip(),
            "receptionnaire": receptionnaire.strip()
        }
        res = requests.post(url, headers=HEADERS, json=payload)
        if res.status_code in (200, 201):
            data = res.json()
            return data[0]['id'] if data else 1
        return None
    except:
        return None

def get_all_transfert_records(limit=200):
    try:
        url = f"{SUPABASE_URL}/transfert_records?select=*&order=date.desc,id.desc&limit={limit}"
        res = requests.get(url, headers=HEADERS)
        return res.json()
    except:
        return []

def delete_transfert_record(record_id):
    try:
        url = f"{SUPABASE_URL}/transfert_records?id=eq.{record_id}"
        res = requests.delete(url, headers=HEADERS)
        return res.status_code in (200, 204)
    except:
        return False
