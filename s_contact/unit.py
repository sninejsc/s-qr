# -*- coding: utf-8 -*-

import qrcode
import base64
import io
import requests
import sys
import odoo
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_qr_code(data):
    if data != "":
        img = qrcode.make(data)
        result = io.BytesIO()
        img.save(result, format='PNG')
        result.seek(0)
        img_bytes = result.read()
        base64_encoded_result_bytes = base64.b64encode(img_bytes)
        base64_encoded_result_str = base64_encoded_result_bytes.decode('ascii')
        return base64_encoded_result_str

def get_host_ip():
    try:
        uuid_local = uuid.getnode()
    except Exception as e:
        logger.error("Cannot get UUID: %s", str(e))
        uuid_local = 0
    return uuid_local

def check_ip_allowed(api_url):
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            licenses = response.json()
            current_ip = str(get_host_ip())
            logger.info("UUID : %s", current_ip)
            for license in licenses:
                if license['ip_address'] == current_ip and license['active']:
                    logger.info("Status: %s", license['active'])
                    return True
            return False
        else:
            logger.error("Cannot access API: HTTP %s", response.status_code)
            return False
    except Exception as e:
        logger.error("Access error HTTP request: %s", str(e))
        return False

def validate_access():
    api_url = odoo.tools.config.get('url_license')
    if not api_url:
        sys.exit("URL API not found in config.")

    if not check_ip_allowed(api_url):
        sys.exit("Deny access because IP address is inactive or not found.")
    else:
        logger.info("Odoo server allows access on IP: %s", get_host_ip())
