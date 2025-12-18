# 🔒 Onion Service Setup Guide
## Quick Setup for MultiSports Betting Platform

---

## 🚀 **QUICK SETUP (Automated)**

Run the setup script:

```bash
sudo ./scripts/setup_onion_service.sh
```

This will:
- ✅ Check/install Tor
- ✅ Create hidden service directory
- ✅ Configure Tor hidden service
- ✅ Generate your .onion address
- ✅ Display your .onion address

**Your .onion address will be displayed at the end.**

---

## 📋 **MANUAL SETUP**

### **Step 1: Install Tor (if not installed)**

```bash
sudo apt-get update
sudo apt-get install tor
```

### **Step 2: Create Hidden Service Directory**

```bash
sudo mkdir -p /var/lib/tor/multisports_betting
sudo chown debian-tor:debian-tor /var/lib/tor/multisports_betting
sudo chmod 700 /var/lib/tor/multisports_betting
```

### **Step 3: Configure Tor**

Edit `/etc/tor/torrc`:

```bash
sudo nano /etc/tor/torrc
```

Add these lines at the end:

```
# MultiSports Betting Platform Hidden Service
HiddenServiceDir /var/lib/tor/multisports_betting/
HiddenServicePort 80 127.0.0.1:8000
HiddenServiceVersion 3
```

**Note:** Ensure your FastAPI app is running on port 8000. If using a different port, change `127.0.0.1:8000` accordingly.

### **Step 4: Restart Tor**

```bash
sudo systemctl restart tor
```

### **Step 5: Get Your .onion Address**

```bash
sudo cat /var/lib/tor/multisports_betting/hostname
```

This will display your .onion address (e.g., `abc123def456.onion`)

**Save this address securely!** This is what you'll share with license holders.

---

## 🔧 **CONFIGURATION OPTIONS**

### **Using Nginx (Recommended)**

If you're using Nginx as a reverse proxy:

1. Configure Nginx to listen on localhost:
```nginx
server {
    listen 127.0.0.1:8000;
    server_name localhost;
    
    location / {
        proxy_pass http://127.0.0.1:8001;  # Your FastAPI app
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. Update Tor config to point to Nginx:
```
HiddenServicePort 80 127.0.0.1:8000
```

### **Direct to FastAPI**

If running FastAPI directly:

1. Ensure FastAPI is listening on 127.0.0.1:8000:
```python
uvicorn.run(app, host="127.0.0.1", port=8000)
```

2. Tor config stays the same:
```
HiddenServicePort 80 127.0.0.1:8000
```

---

## 🧪 **TESTING**

### **Test Locally:**

1. Start your FastAPI app
2. Start Tor service: `sudo systemctl start tor`
3. Open Tor Browser
4. Navigate to: `http://[YOUR-ONION-ADDRESS].onion`

You should see your platform!

### **Troubleshooting:**

**Can't access .onion address:**
- Check Tor service: `sudo systemctl status tor`
- Check Tor logs: `sudo journalctl -u tor -n 50`
- Ensure FastAPI app is running on port 8000
- Verify hidden service directory permissions

**Hidden service not generating:**
- Check Tor logs for errors
- Verify torrc configuration is correct
- Ensure directory permissions are correct (700, owned by debian-tor)

---

## 🔐 **SECURITY NOTES**

1. **Directory Permissions**: The hidden service directory should be 700 and owned by debian-tor user
2. **Private Key**: Never share the private key in `/var/lib/tor/multisports_betting/`
3. **Onion Address**: Share only with license holders
4. **Access Control**: Use authentication (JWT tokens) even on .onion domain

---

## 📝 **FOR LICENSE HOLDERS**

When a license is activated, provide:

1. The .onion address
2. Tor Browser download link: https://www.torproject.org/download/
3. Quick setup instructions:
   - Download and install Tor Browser
   - Open Tor Browser
   - Navigate to: `http://[YOUR-ONION-ADDRESS].onion`
   - Login with credentials

---

## 🎯 **BEST PRACTICES**

1. **Backup .onion Address**: Save it securely (if you lose it, you'll need to regenerate)
2. **Monitor Service**: Check Tor service status regularly
3. **Update Regularly**: Keep Tor updated: `sudo apt-get update && sudo apt-get upgrade tor`
4. **Access Logs**: Monitor access (anonymized, but helpful for support)

---

**🔒 Your platform is now accessible via secure .onion domain!**


