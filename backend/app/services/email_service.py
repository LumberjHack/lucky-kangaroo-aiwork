"""
Service d'email pour Lucky Kangaroo
"""

from flask import current_app, render_template_string
from flask_mail import Mail, Message
from app import mail

class EmailService:
    """Service de gestion des emails"""
    
    def __init__(self):
        self.mail = mail
    
    def send_verification_email(self, email, token):
        """Envoyer un email de vérification"""
        try:
            verification_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/auth/verify-email?token={token}"
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Vérification de votre compte Lucky Kangaroo</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #8B5CF6, #3B82F6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .button { display: inline-block; background: linear-gradient(135deg, #8B5CF6, #3B82F6); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🦘 Lucky Kangaroo</h1>
                        <p>Vérifiez votre compte</p>
                    </div>
                    <div class="content">
                        <h2>Bienvenue sur Lucky Kangaroo !</h2>
                        <p>Merci de vous être inscrit sur notre plateforme d'échange d'objets et de services.</p>
                        <p>Pour activer votre compte, cliquez sur le bouton ci-dessous :</p>
                        <a href="{{ verification_url }}" class="button">Vérifier mon compte</a>
                        <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :</p>
                        <p><a href="{{ verification_url }}">{{ verification_url }}</a></p>
                        <p>Ce lien expire dans 24 heures.</p>
                        <p>L'équipe Lucky Kangaroo</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Lucky Kangaroo. Tous droits réservés.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject="Vérifiez votre compte Lucky Kangaroo",
                recipients=[email],
                html=render_template_string(html_template, verification_url=verification_url)
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erreur lors de l'envoi de l'email de vérification: {str(e)}")
            return False
    
    def send_password_reset_email(self, email, token):
        """Envoyer un email de réinitialisation de mot de passe"""
        try:
            reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/auth/reset-password?token={token}"
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Réinitialisation de votre mot de passe Lucky Kangaroo</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #8B5CF6, #3B82F6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .button { display: inline-block; background: linear-gradient(135deg, #8B5CF6, #3B82F6); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                    .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🦘 Lucky Kangaroo</h1>
                        <p>Réinitialisation de mot de passe</p>
                    </div>
                    <div class="content">
                        <h2>Demande de réinitialisation</h2>
                        <p>Vous avez demandé à réinitialiser votre mot de passe Lucky Kangaroo.</p>
                        <p>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</p>
                        <a href="{{ reset_url }}" class="button">Réinitialiser mon mot de passe</a>
                        <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :</p>
                        <p><a href="{{ reset_url }}">{{ reset_url }}</a></p>
                        <div class="warning">
                            <strong>⚠️ Important :</strong> Si vous n'avez pas demandé cette réinitialisation, ignorez cet email. Votre mot de passe ne sera pas modifié.
                        </div>
                        <p>Ce lien expire dans 1 heure.</p>
                        <p>L'équipe Lucky Kangaroo</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Lucky Kangaroo. Tous droits réservés.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject="Réinitialisation de votre mot de passe Lucky Kangaroo",
                recipients=[email],
                html=render_template_string(html_template, reset_url=reset_url)
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erreur lors de l'envoi de l'email de réinitialisation: {str(e)}")
            return False
    
    def send_exchange_notification(self, email, exchange_data):
        """Envoyer une notification d'échange"""
        try:
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Nouvelle proposition d'échange - Lucky Kangaroo</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #8B5CF6, #3B82F6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .button { display: inline-block; background: linear-gradient(135deg, #8B5CF6, #3B82F6); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                    .exchange-details { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🦘 Lucky Kangaroo</h1>
                        <p>Nouvelle proposition d'échange</p>
                    </div>
                    <div class="content">
                        <h2>Vous avez reçu une nouvelle proposition !</h2>
                        <p>{{ sender_name }} souhaite échanger avec vous.</p>
                        
                        <div class="exchange-details">
                            <h3>Détails de la proposition :</h3>
                            <p><strong>Objet proposé :</strong> {{ proposed_item }}</p>
                            <p><strong>Message :</strong> {{ message }}</p>
                        </div>
                        
                        <a href="{{ exchange_url }}" class="button">Voir la proposition</a>
                        
                        <p>L'équipe Lucky Kangaroo</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Lucky Kangaroo. Tous droits réservés.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            exchange_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/exchanges/{exchange_data['id']}"
            
            msg = Message(
                subject="Nouvelle proposition d'échange - Lucky Kangaroo",
                recipients=[email],
                html=render_template_string(
                    html_template, 
                    sender_name=exchange_data.get('sender_name', 'Un utilisateur'),
                    proposed_item=exchange_data.get('proposed_item', 'Un objet'),
                    message=exchange_data.get('message', ''),
                    exchange_url=exchange_url
                )
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erreur lors de l'envoi de la notification d'échange: {str(e)}")
            return False
    
    def send_welcome_email(self, email, username):
        """Envoyer un email de bienvenue"""
        try:
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Bienvenue sur Lucky Kangaroo !</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #8B5CF6, #3B82F6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .button { display: inline-block; background: linear-gradient(135deg, #8B5CF6, #3B82F6); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                    .feature { background: white; padding: 15px; border-radius: 5px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🦘 Lucky Kangaroo</h1>
                        <p>Bienvenue {{ username }} !</p>
                    </div>
                    <div class="content">
                        <h2>Félicitations ! Votre compte est maintenant actif.</h2>
                        <p>Vous pouvez maintenant profiter de toutes les fonctionnalités de Lucky Kangaroo :</p>
                        
                        <div class="feature">
                            <strong>🔄 Échangez vos objets</strong><br>
                            Publiez vos objets et trouvez des échanges intéressants
                        </div>
                        
                        <div class="feature">
                            <strong>🤖 IA intelligente</strong><br>
                            Notre IA vous aide à estimer la valeur et à trouver des matches
                        </div>
                        
                        <div class="feature">
                            <strong>🌍 Géolocalisation</strong><br>
                            Trouvez des échanges près de chez vous
                        </div>
                        
                        <div class="feature">
                            <strong>💬 Chat sécurisé</strong><br>
                            Communiquez en toute sécurité avec les autres utilisateurs
                        </div>
                        
                        <a href="{{ dashboard_url }}" class="button">Commencer à échanger</a>
                        
                        <p>L'équipe Lucky Kangaroo</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Lucky Kangaroo. Tous droits réservés.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            dashboard_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/dashboard"
            
            msg = Message(
                subject="Bienvenue sur Lucky Kangaroo !",
                recipients=[email],
                html=render_template_string(html_template, username=username, dashboard_url=dashboard_url)
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erreur lors de l'envoi de l'email de bienvenue: {str(e)}")
            return False
