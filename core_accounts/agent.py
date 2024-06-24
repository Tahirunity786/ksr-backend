from django.core.mail import send_mail
from django.conf import settings

class MailAgent:

    def __init__(self):
        self.from_email = settings.EMAIL_HOST_USER
    
    def greeting(self, user):
        subject = 'Welcome to Cultured Mentor'
        logo_url = "https://sijar87020.pythonanywhere.com/static/media/Asset%20238@2x.png"  
        message = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    margin: auto;
                }}
                .header {{
                    text-align: center;
                }}
                .header img {{
                    max-width: 150px;
                }}
                .content {{
                    margin-top: 20px;
                }}
                .content p {{
                    font-size: 16px;
                    line-height: 1.5;
                    color: #333333;
                }}
                .footer {{
                    margin-top: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #777777;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="{logo_url}" alt="Cultured Mentor Logo">
                </div>
                <div class="content">
                    <p>Dear {user.first_name},</p>
                    <p>We are delighted to welcome you to Cultured Mentor!</p>
                    <p>Thank you for registering with us. We are committed to providing you with the best services and a seamless experience. Whether you are here to explore, learn, or achieve new milestones, we are here to support you every step of the way.</p>
                    <p>To help you get started, here are a few resources you might find useful:</p>
                    <ul>
                        <li><a href="https://www.yourwebsite.com/user-guide">User Guide</a></li>
                        <li><a href="https://www.yourwebsite.com/faq">FAQ</a></li>
                        <li><a href="mailto:tahirunity786@gmail.com">Customer Support</a></li>
                    </ul>
                    <p>If you have any questions or need assistance, please do not hesitate to contact our support team at <a href="mailto:[Support Email Address]">[Support Email Address]</a> or call us at [Support Phone Number]. We are here to help you 24/7.</p>
                    <p>Once again, welcome to our community! We look forward to a successful journey together.</p>
                </div>
                <div class="footer">
                    <p>Best Regards,</p>
                    <p>Cultured Mentor Team</p>
                    <p><a href="https://www.yourwebsite.com">www.yourwebsite.com</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        from_email = self.from_email
        recipient_list = [user.email]  
        send_mail(subject, '', from_email, recipient_list, html_message=message)
        return True
