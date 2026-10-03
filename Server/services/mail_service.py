import asyncio
import smtplib

from email.message import EmailMessage

from config.settings import settings


def _send_email_sync(
    to: str,
    subject: str,
    body: str,
) -> None:

    if not settings.smtp_host:

        print("\n📨 DEVELOPMENT EMAIL")
        print("--------------------")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(body)
        print("--------------------\n")

        return

    message = EmailMessage()

    message["From"] = settings.smtp_from

    message["To"] = to

    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(
        settings.smtp_host,
        settings.smtp_port,
    ) as smtp:

        smtp.starttls()

        if settings.smtp_username and settings.smtp_password:

            smtp.login(
                settings.smtp_username,
                settings.smtp_password,
            )

        smtp.send_message(message)


async def send_email(
    to: str,
    subject: str,
    body: str,
) -> None:

    await asyncio.to_thread(
        _send_email_sync,
        to,
        subject,
        body,
    )


async def send_otp_email(
    email: str,
    otp: str,
) -> None:

    await send_email(
        email,
        "Pastor's Pulpit verification code",
        f"Your verification code is: {otp}",
    )


async def send_password_reset_email(
    email: str,
    token: str,
) -> None:

    reset_url = f"{settings.client_url}" f"/reset-password?token={token}"

    await send_email(
        email,
        "Pastor's Pulpit password reset",
        f"Reset your password here:\n{reset_url}",
    )
