"""
CMI (Centre Monétique Interbancaire) Payment Gateway
======================================================
Le standard de paiement en ligne au Maroc.
Utilisé par : Hôtels Marriott, Sofitel, Hyatt Maroc, Royal Air Maroc,
              ONCF, Marjane, Carrefour Maroc, Booking.com Maroc...

Protocol: Ingenico/Worldline e-Commerce (3-D Secure)
Documentation: https://www.cmi.co.ma/

Configuration requise (variables d'environnement) :
- CMI_CLIENT_ID      : Identifiant marchand (fourni par CMI/votre banque)
- CMI_STORE_KEY      : Clé secrète du magasin
- CMI_BASE_URL       : URL de base du site (ex: https://www.hotel-alandalus.ma)
- CMI_TEST_MODE      : "True" pour le mode simulation
"""

import hashlib
import hmac
import json
import logging
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)

# ── CMI Gateway URLs ──────────────────────────────────
CMI_PRODUCTION_URL = "https://payment.cmi.co.ma/fim/est3Dgate"
CMI_TEST_URL       = "https://testpayment.cmi.co.ma/fim/est3Dgate"

# ── Currency code ─────────────────────────────────────
MAD_CURRENCY_CODE = "504"   # ISO 4217 code for Moroccan Dirham

# ── Default store type ────────────────────────────────
STORE_TYPE = "pay_hosting"


def get_cmi_config():
    """Load CMI config from Django settings / env variables."""
    return {
        'client_id':  getattr(settings, 'CMI_CLIENT_ID',  'TEST_MERCHANT_001'),
        'store_key':  getattr(settings, 'CMI_STORE_KEY',  'TEST_SECRET_KEY_CHANGE_IN_PROD'),
        'base_url':   getattr(settings, 'CMI_BASE_URL',   'http://127.0.0.1:8000'),
        'test_mode':  getattr(settings, 'CMI_TEST_MODE',  True),
        'lang':       getattr(settings, 'CMI_LANG',       'fr'),
        'currency':   MAD_CURRENCY_CODE,
        'store_type': STORE_TYPE,
    }


def _compute_hash(params: dict, store_key: str) -> str:
    """
    CMI uses SHA-512 HMAC to sign the payment request.
    Parameters are sorted alphabetically and concatenated.
    """
    # Sort keys alphabetically (CMI requirement)
    sorted_keys = sorted(params.keys())
    hash_str = store_key
    for key in sorted_keys:
        if key not in ('encoding', 'hash'):
            hash_str += str(params[key])
    hash_str += store_key

    h = hashlib.sha512(hash_str.encode('utf-8')).hexdigest().upper()
    return h


def build_payment_form(booking, order_id: str, request=None) -> dict:
    """
    Build the CMI payment form parameters.
    Returns a dict with all fields to POST to CMI gateway.
    """
    cfg = get_cmi_config()
    base = cfg['base_url'].rstrip('/')

    # Callback URLs
    ok_url   = base + '/paiement/retour/succes/'
    fail_url = base + '/paiement/retour/echec/'
    callback = base + '/paiement/callback/'   # Server-to-server notification

    # Amount: in MAD, 2 decimal places, no separator
    amount = f"{float(booking.total_price):.2f}"

    params = {
        'clientid':       cfg['client_id'],
        'storetype':      cfg['store_type'],
        'amount':         amount,
        'currency':       cfg['currency'],
        'oid':            order_id,
        'okUrl':          ok_url,
        'failUrl':        fail_url,
        'callbackUrl':    callback,
        'encoding':       'UTF-8',
        'lang':           cfg['lang'],
        'rnd':            str(booking.id),
        'email':          booking.email,
        'BillToName':     booking.name,
        'BillToEmail':    booking.email,
        'BillToPhone':    booking.phone or '',
        'description':    f"Réservation {booking.room.name} — {booking.check_in} au {booking.check_out}",
        'tel':            booking.phone or '',
    }

    # Compute hash signature
    params['hash'] = _compute_hash(params, cfg['store_key'])

    gateway_url = CMI_TEST_URL if cfg['test_mode'] else CMI_PRODUCTION_URL

    return {
        'gateway_url': gateway_url,
        'params':      params,
        'is_test':     cfg['test_mode'],
    }


def verify_callback(post_data: dict) -> dict:
    """
    Verify the CMI callback/notification signature.
    Returns dict with verified=True/False and payment status.
    """
    cfg = get_cmi_config()
    received_hash = post_data.get('hash', '')

    # Rebuild hash without the 'hash' field itself
    check_params = {k: v for k, v in post_data.items() if k != 'hash'}
    expected_hash = _compute_hash(check_params, cfg['store_key'])

    if received_hash.upper() != expected_hash.upper():
        logger.warning(f"CMI hash mismatch! Received: {received_hash[:20]}... Expected: {expected_hash[:20]}...")
        return {'verified': False, 'reason': 'Hash mismatch'}

    # CMI response codes
    resp_code = post_data.get('ProcReturnCode', '')
    approved  = resp_code == '00'

    return {
        'verified':       True,
        'approved':       approved,
        'order_id':       post_data.get('oid', ''),
        'transaction_id': post_data.get('TransId', ''),
        'auth_code':      post_data.get('AuthCode', ''),
        'response_code':  resp_code,
        'response_msg':   post_data.get('ErrMsg', ''),
        'card_last4':     post_data.get('MaskedPan', '')[-4:] if post_data.get('MaskedPan') else '',
        'card_brand':     post_data.get('CardType', ''),
        'amount':         post_data.get('amount', ''),
    }


def get_response_message(response_code: str) -> str:
    """Human-readable CMI response code messages (French)."""
    messages = {
        '00': 'Paiement approuvé',
        '01': 'Contacter l\'émetteur',
        '03': 'Commerçant invalide',
        '04': 'Carte saisie — contacter la banque',
        '05': 'Paiement refusé',
        '12': 'Transaction invalide',
        '13': 'Montant invalide',
        '14': 'Numéro de carte invalide',
        '25': 'Enregistrement introuvable',
        '30': 'Erreur de format',
        '31': 'Banque non supportée',
        '33': 'Carte expirée',
        '34': 'Fraude suspectée',
        '41': 'Carte perdue',
        '43': 'Carte volée',
        '51': 'Provision insuffisante',
        '54': 'Carte expirée',
        '55': 'Code PIN incorrect',
        '57': 'Transaction non autorisée',
        '58': 'Transaction non autorisée pour ce terminal',
        '61': 'Plafond de retrait dépassé',
        '62': 'Carte restreinte',
        '65': 'Nombre d\'utilisation dépassé',
        '75': 'Tentatives PIN dépassées',
        '76': 'Code PIN incorrect — contacter la banque',
        '89': 'Code PIN non valide',
        '91': 'Banque temporairement indisponible',
        '94': 'Transaction dupliquée',
        '96': 'Erreur système',
    }
    return messages.get(response_code, f'Code erreur : {response_code}')
