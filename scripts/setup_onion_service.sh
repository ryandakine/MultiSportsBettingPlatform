#!/bin/bash
# 🔒 Setup Tor Hidden Service for MultiSports Betting Platform
# This script configures a .onion domain for the platform

set -e

echo "🔒 Setting up Tor Hidden Service for MultiSports Betting Platform..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (sudo)"
    exit 1
fi

# Check if Tor is installed
if ! command -v tor &> /dev/null; then
    echo "⚠️  Tor is not installed. Installing..."
    apt-get update
    apt-get install -y tor
fi

echo "✅ Tor is installed"

# Configuration directory
HIDDEN_SERVICE_DIR="/var/lib/tor/multisports_betting"
TORRC_PATH="/etc/tor/torrc"

# Create hidden service directory
echo "📁 Creating hidden service directory..."
mkdir -p "$HIDDEN_SERVICE_DIR"
chown debian-tor:debian-tor "$HIDDEN_SERVICE_DIR"
chmod 700 "$HIDDEN_SERVICE_DIR"

# Backup existing torrc
if [ -f "$TORRC_PATH" ]; then
    cp "$TORRC_PATH" "$TORRC_PATH.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backed up existing torrc"
fi

# Check if hidden service is already configured
if grep -q "HiddenServiceDir /var/lib/tor/multisports_betting" "$TORRC_PATH" 2>/dev/null; then
    echo "⚠️  Hidden service already configured in torrc"
    echo "   Checking if it needs updates..."
else
    echo "➕ Adding hidden service configuration to torrc..."
    cat >> "$TORRC_PATH" << 'EOF'

# MultiSports Betting Platform Hidden Service
HiddenServiceDir /var/lib/tor/multisports_betting/
HiddenServicePort 80 127.0.0.1:8000
HiddenServiceVersion 3
EOF
    echo "✅ Added hidden service configuration"
fi

# Restart Tor to generate .onion address
echo "🔄 Restarting Tor service..."
systemctl restart tor

# Wait a moment for Tor to generate the address
sleep 3

# Check if .onion address was generated
if [ -f "$HIDDEN_SERVICE_DIR/hostname" ]; then
    ONION_ADDRESS=$(cat "$HIDDEN_SERVICE_DIR/hostname")
    echo ""
    echo "✅ Hidden service configured successfully!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔒 YOUR .ONION ADDRESS:"
    echo "   $ONION_ADDRESS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📋 NEXT STEPS:"
    echo "   1. Ensure your FastAPI app is running on port 8000"
    echo "   2. Test access: Open Tor Browser and navigate to:"
    echo "      http://$ONION_ADDRESS"
    echo "   3. Share this address only with license holders"
    echo ""
    echo "🔧 Configuration:"
    echo "   - Service directory: $HIDDEN_SERVICE_DIR"
    echo "   - Internal port: 80"
    echo "   - Maps to: 127.0.0.1:8000 (your FastAPI app)"
    echo ""
    echo "📝 Note: Save this .onion address securely!"
    echo "   It will be shared with license holders after approval."
    echo ""
else
    echo "❌ Failed to generate .onion address"
    echo "   Check Tor logs: journalctl -u tor -n 50"
    exit 1
fi

# Show Tor status
echo "📊 Tor service status:"
systemctl status tor --no-pager -l | head -n 10

echo ""
echo "✅ Setup complete!"


