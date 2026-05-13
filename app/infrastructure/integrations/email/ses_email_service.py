from app.domain.ports.email_ports import EmailPort
from app.infrastructure.database.repositories.auth_repository import AuthRepo
from app.core.config import Settings
import boto3
from botocore.exceptions import ClientError
from app.core.constants import EmailConstants

settings = Settings()


class SeSEmailService(EmailPort):

    def __init__(self):
        self.ses = boto3.client(
            "ses",
            region_name="ap-southeast-2",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def send_email(self, to_email: str, subject: str, body: str):
        try:
            self.ses.send_email(
                Source=EmailConstants.SENDER_EMAIL,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                },
            )
            return True
        except Exception as e:
            return False

    def send_otp_verification_mail(self, to_email: str, otp: str):

        subject = "Verify your email address"
        body = f"""
        Hello,

        Your verification code is:

        {otp}

        This code will expire in 5 minutes.

        If you did not request this verification, please ignore this email.

        Thanks,
        PLG Team
        """
        return self.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
        )
