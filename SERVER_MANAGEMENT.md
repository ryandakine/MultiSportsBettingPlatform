# Server Management Guide

## ✅ Server is now running as a systemd service

The server will:
- ✅ Start automatically on boot
- ✅ Restart automatically if it crashes
- ✅ Stay running in the background
- ✅ Log to systemd journal

## Service Management Commands

### Check Status
```bash
sudo systemctl status multisports-betting
```

### View Logs
```bash
# Recent logs
sudo journalctl -u multisports-betting -n 50 --no-pager

# Follow logs in real-time
sudo journalctl -u multisports-betting -f

# Logs from today
sudo journalctl -u multisports-betting --since today
```

### Start/Stop/Restart
```bash
sudo systemctl start multisports-betting
sudo systemctl stop multisports-betting
sudo systemctl restart multisports-betting
```

### Enable/Disable Auto-Start on Boot
```bash
sudo systemctl enable multisports-betting   # Enable auto-start
sudo systemctl disable multisports-betting  # Disable auto-start
```

## Configuration

The service file is at: `/etc/systemd/system/multisports-betting.service`

To edit environment variables:
```bash
sudo systemctl edit multisports-betting
# Add override settings in the editor
```

Or edit the service file directly:
```bash
sudo nano /etc/systemd/system/multisports-betting.service
sudo systemctl daemon-reload
sudo systemctl restart multisports-betting
```

## Automated Tasks

The server automatically runs:
- **Daily Prediction Generation**: Runs at 8 AM UTC (or immediately if server starts after 8 AM)
- **Autonomous Betting**: Places bets once per day when predictions are available
- **Bet Settlement**: Runs hourly to settle pending bets

## No Manual Intervention Needed!

Once enabled, the system runs completely automatically. You don't need to:
- ❌ Start the server manually
- ❌ Restart it daily
- ❌ Monitor it constantly (unless you want to)

The system will:
- ✅ Start on boot
- ✅ Generate predictions daily
- ✅ Place bets automatically
- ✅ Settle bets hourly
- ✅ Restart if it crashes

