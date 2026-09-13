"""
alert_system.py - BDI Price Alert & Notification System.
Manages user-configured threshold alerts with email delivery via SMTP.
"""

import json
import os
import smtplib
import uuid
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ALERTS_FILE = os.path.join(os.path.dirname(__file__), 'models', 'alerts.json')

# SMTP configuration (user should update these for production)
SMTP_CONFIG = {
    'server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
    'port': int(os.environ.get('SMTP_PORT', '587')),
    'username': os.environ.get('SMTP_USERNAME', ''),
    'password': os.environ.get('SMTP_PASSWORD', ''),
    'from_email': os.environ.get('SMTP_FROM', 'freightiq@alerts.com'),
}


class AlertManager:
    """Manages BDI price threshold alerts with persistent storage."""
    
    def __init__(self):
        self.alerts = self._load_alerts()
    
    def _load_alerts(self):
        """Load alerts from JSON file."""
        if os.path.exists(ALERTS_FILE):
            try:
                with open(ALERTS_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []
    
    def _save_alerts(self):
        """Persist alerts to JSON file."""
        try:
            os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
            with open(ALERTS_FILE, 'w') as f:
                json.dump(self.alerts, f, indent=2)
        except IOError:
            pass
    
    def add_alert(self, email, threshold, direction='below', label=''):
        """
        Register a new BDI price alert.
        
        Args:
            email: Recipient email address
            threshold: BDI price threshold value
            direction: 'below' (alert when BDI drops below) or 'above' (alert when rises above)
            label: Optional descriptive label
            
        Returns:
            dict: The created alert object
        """
        alert = {
            'id': str(uuid.uuid4())[:8],
            'email': email,
            'threshold': float(threshold),
            'direction': direction,
            'label': label or f"BDI {'drops below' if direction == 'below' else 'rises above'} {threshold}",
            'created_at': datetime.now().isoformat(),
            'is_active': True,
            'triggered_count': 0,
            'last_triggered': None
        }
        self.alerts.append(alert)
        self._save_alerts()
        return alert
    
    def remove_alert(self, alert_id):
        """Remove an alert by ID."""
        self.alerts = [a for a in self.alerts if a['id'] != alert_id]
        self._save_alerts()
        return True
    
    def get_all_alerts(self):
        """Return all alerts."""
        return self.alerts
    
    def get_active_alerts(self):
        """Return only active alerts."""
        return [a for a in self.alerts if a.get('is_active', True)]
    
    def check_alerts(self, current_price, forecast_prices=None):
        """
        Evaluate all active alerts against current BDI price and forecasts.
        
        Args:
            current_price: Current BDI settlement price
            forecast_prices: Optional list of predicted future prices
            
        Returns:
            list: Alerts that were triggered
        """
        triggered = []
        
        for alert in self.alerts:
            if not alert.get('is_active', True):
                continue
            
            threshold = alert['threshold']
            direction = alert['direction']
            
            # Check current price
            is_triggered = False
            trigger_price = current_price
            trigger_source = 'current_settlement'
            
            if direction == 'below' and current_price <= threshold:
                is_triggered = True
            elif direction == 'above' and current_price >= threshold:
                is_triggered = True
            
            # Also check forecasts for early warnings
            if not is_triggered and forecast_prices:
                for i, fp in enumerate(forecast_prices[:7]):  # Check 7-day forecast
                    price = fp if isinstance(fp, (int, float)) else fp.get('predicted_price', 0)
                    if direction == 'below' and price <= threshold:
                        is_triggered = True
                        trigger_price = price
                        trigger_source = f'forecast_day_{i+1}'
                        break
                    elif direction == 'above' and price >= threshold:
                        is_triggered = True
                        trigger_price = price
                        trigger_source = f'forecast_day_{i+1}'
                        break
            
            if is_triggered:
                alert['triggered_count'] = alert.get('triggered_count', 0) + 1
                alert['last_triggered'] = datetime.now().isoformat()
                
                triggered.append({
                    'alert': alert,
                    'trigger_price': trigger_price,
                    'trigger_source': trigger_source,
                    'current_price': current_price
                })
                
                # Send email notification
                self._send_notification(alert, current_price, trigger_price, trigger_source)
        
        if triggered:
            self._save_alerts()
        
        return triggered
    
    def _send_notification(self, alert, current_price, trigger_price, trigger_source):
        """Send email notification for a triggered alert."""
        subject = f"[FreightIQ ALERT] BDI {alert['direction'].upper()} {alert['threshold']}"
        
        body = f"""
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        BALTIC DRY INDEX - PRICE ALERT TRIGGERED
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        Alert:       {alert['label']}
        Direction:   {alert['direction'].upper()}
        Threshold:   {alert['threshold']:,.2f} BDI
        
        Current BDI: {current_price:,.2f}
        Trigger:     {trigger_price:,.2f} ({trigger_source})
        Time:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ACTION RECOMMENDED:
        - Review current freight market conditions
        - Consider {'entering the market' if alert['direction'] == 'below' else 'hedging positions'}
        - Visit http://localhost:8000 for full analysis
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        FreightIQ Automated Alert System
        """
        
        # Attempt email delivery
        if SMTP_CONFIG['username'] and SMTP_CONFIG['password']:
            try:
                msg = MIMEMultipart()
                msg['From'] = SMTP_CONFIG['from_email']
                msg['To'] = alert['email']
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                
                with smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port']) as server:
                    server.starttls()
                    server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
                    server.send_message(msg)
                
                print(f"[ALERT] Email sent to {alert['email']}: {subject}")
                return True
            except Exception as e:
                print(f"[ALERT] Email delivery failed: {e}")
                return False
        else:
            # Log to console if SMTP not configured
            print(f"[ALERT TRIGGERED] {subject}")
            print(f"  Recipient: {alert['email']}")
            print(f"  Current BDI: {current_price:,.2f} | Threshold: {alert['threshold']:,.2f}")
            print(f"  (Configure SMTP_USERNAME/SMTP_PASSWORD env vars for email delivery)")
            return False


# Global singleton
alert_manager = AlertManager()
