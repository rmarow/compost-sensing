#!/usr/bin/env python3
"""
Notification Module
Handles email alerts for threshold violations
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AlertNotifier:
    """Handles sending alert notifications via email"""
    
    def __init__(self, config):
        self.config = config
        self.email_enabled = config.EMAIL_ALERTS_ENABLED
        
    def send_alert(self, alert_data):
        """
        Send alert notification via configured methods
        
        alert_data should contain:
        - sensor_name: Name of sensor
        - alert_type: Type of alert (temp_high, temp_low, etc)
        - message: Alert message
        - value: Current value
        - threshold: Threshold that was crossed
        - timestamp: When alert occurred
        """
        
        success = False
        
        # Send email alerts
        if self.email_enabled:
            email_sent = self._send_email(alert_data)
            success = success or email_sent

        return success
    
    def _send_email(self, alert_data):
        """Send email alert"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 Farm Alert: {alert_data['sensor_name']}"
            msg['From'] = self.config.SMTP_USERNAME
            msg['To'] = ', '.join(self.config.ALERT_RECIPIENTS)
            
            # Create email body
            text_body = self._create_text_body(alert_data)
            html_body = self._create_html_body(alert_data)
            
            # Attach both plain text and HTML versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email alert sent: {alert_data['message']}")
            return True
            
        except Exception as error:
            logger.error(f"Failed to send email alert: {error}")
            return False
    
    def _create_text_body(self, alert_data):
        """Create plain text email body"""
        return f"""
Milk and Honey Farm - Compost Monitoring Alert
================================================

ALERT: {alert_data['message']}

Sensor: {alert_data['sensor_name']}
Alert Type: {alert_data['alert_type']}
Current Value: {alert_data['value']}
Threshold: {alert_data['threshold']}
Time: {alert_data['timestamp'].strftime('%Y-%m-%d %I:%M:%S %p')}

Action may be required. Check the dashboard for more details:
http://raspberrypi.local:5000

This is an automated alert from the farm monitoring system.
"""
    
    def _create_html_body(self, alert_data):
        """Create HTML email body"""
        
        # Determine alert color and emoji
        if 'high' in alert_data['alert_type']:
            color = '#dc2626'  # Red
            emoji = '🔥'
        else:
            color = '#2563eb'  # Blue
            emoji = '❄️'
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: {color}; color: white; padding: 20px; border-radius: 5px; }}
        .alert-box {{ background: #f3f4f6; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid {color}; }}
        .detail {{ margin: 10px 0; }}
        .label {{ font-weight: bold; }}
        .value {{ color: {color}; font-size: 1.2em; }}
        .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 0.9em; }}
        a {{ color: {color}; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{emoji} Farm Monitoring Alert</h1>
            <p>Milk and Honey Farm - Boulder JCC</p>
        </div>
        
        <div class="alert-box">
            <h2>Alert: {alert_data['sensor_name']}</h2>
            <p style="font-size: 1.1em;">{alert_data['message']}</p>
            
            <div class="detail">
                <span class="label">Alert Type:</span> {alert_data['alert_type'].replace('_', ' ').title()}
            </div>
            
            <div class="detail">
                <span class="label">Current Value:</span> 
                <span class="value">{alert_data['value']}</span>
            </div>
            
            <div class="detail">
                <span class="label">Threshold:</span> {alert_data['threshold']}
            </div>
            
            <div class="detail">
                <span class="label">Time:</span> {alert_data['timestamp'].strftime('%Y-%m-%d %I:%M:%S %p')}
            </div>
        </div>
        
        <p>
            <a href="http://raspberrypi.local:5000" style="display: inline-block; background: {color}; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                View Dashboard
            </a>
        </p>
        
        <div class="footer">
            <p>This is an automated alert from the Milk and Honey Farm monitoring system.</p>
            <p>To adjust alert thresholds, edit config.py on your Raspberry Pi.</p>
        </div>
    </div>
</body>
</html>
"""

def test_notifications(config):
    """Test notification system with a sample alert"""
    
    print("Testing Farm Monitoring Notification System")
    print("=" * 60)
    
    notifier = AlertNotifier(config)
    
    # Create test alert
    test_alert = {
        'sensor_name': 'Bin 1 - Compost Core',
        'alert_type': 'temp_high',
        'message': 'Temperature too high: 68.5°C',
        'value': 68.5,
        'threshold': 65,
        'timestamp': datetime.now()
    }
    
    print("\nSending test alert...")
    print(f"Email enabled: {config.EMAIL_ALERTS_ENABLED}")
    print(f"Recipients: {config.ALERT_RECIPIENTS}")
    
    if config.EMAIL_ALERTS_ENABLED:
        success = notifier.send_alert(test_alert)
        if success:
            print("\n✅ Test alert sent successfully!")
            print("Check your email for the test message.")
        else:
            print("\n❌ Failed to send test alert. Check logs for details.")
    else:
        print("\n⚠️  Email alerts not enabled.")
        print("Set EMAIL_ALERTS_ENABLED = True in config.py")
    
    print("=" * 60)

if __name__ == "__main__":
    # Test the notification system
    import config
    test_notifications(config)
