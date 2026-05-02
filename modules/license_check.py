import os
import json
import uuid
import requests
import tkinter as tk
from tkinter import messagebox, simpledialog

LICENSE_FILE = os.path.join(os.path.expanduser("~"), ".dtechcam_license")
VERIFY_URL = "https://services.dtechplatform.com.ng/api/cam/verify-license"

def get_device_id():
    try:
        return str(uuid.getnode())
    except:
        return "unknown-device"

def load_stored_license():
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_license(key):
    with open(LICENSE_FILE, "w") as f:
        json.dump({"licenseKey": key}, f)

def verify_license(license_key):
    device_id = get_device_id()
    try:
        resp = requests.post(VERIFY_URL, json={"licenseKey": license_key, "deviceId": device_id}, timeout=10)
        return resp.json()
    except Exception as e:
        return {"valid": False, "reason": "Could not connect to license server. Check your internet."}

def check_license():
    stored = load_stored_license()
    key = stored.get("licenseKey", "")
    if key:
        result = verify_license(key)
        if result.get("valid"):
            print(f"[DTech Cam] License valid — Plan: {result.get('plan')} | Days left: {result.get('daysLeft')}")
            return True
    # Show license input dialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    while True:
        key = simpledialog.askstring(
            "DTech Cam — License Key",
            "Enter your DTech Cam license key:\n(Purchased at cam.dtechplatform.com.ng)",
            parent=root
        )
        if not key:
            messagebox.showerror("DTech Cam", "License key required to use DTech Cam.\nVisit cam.dtechplatform.com.ng to purchase.")
            root.destroy()
            return False
        key = key.strip()
        result = verify_license(key)
        if result.get("valid"):
            save_license(key)
            messagebox.showinfo("DTech Cam", f"License activated!\nPlan: {result.get('plan')}\nDays left: {result.get('daysLeft')}")
            root.destroy()
            return True
        else:
            reason = result.get("reason", "Invalid license key")
            retry = messagebox.askretrycancel("DTech Cam — Invalid License", f"{reason}\n\nTry again?")
            if not retry:
                root.destroy()
                return False
