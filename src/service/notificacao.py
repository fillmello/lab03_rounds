import logging
import smtplib
from email.message import EmailMessage

from src.settings import settings

logger = logging.getLogger("moeda.email")


def _message(to: str, subject: str, body: str) -> EmailMessage:
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    return message


def moeda_recebida(to: str, aluno: str, professor: str, quantidade: int, motivo: str) -> EmailMessage:
    return _message(
        to,
        f"Você recebeu {quantidade} moedas",
        f"Olá, {aluno}!\n\nO professor {professor} enviou {quantidade} moedas para você.\n"
        f"Motivo: {motivo}\n",
    )


def cupom_aluno(to: str, aluno: str, vantagem: str, empresa: str, codigo: str) -> EmailMessage:
    return _message(
        to,
        f"Cupom: {vantagem}",
        f"Olá, {aluno}!\n\nSua troca de \"{vantagem}\" ({empresa}) foi confirmada.\n"
        f"Apresente o código abaixo na troca presencial:\n\n{codigo}\n",
    )


def cupom_parceiro(to: str, empresa: str, vantagem: str, aluno: str, codigo: str) -> EmailMessage:
    return _message(
        to,
        f"Nova troca: {vantagem}",
        f"Olá, {empresa}!\n\n{aluno} trocou moedas por \"{vantagem}\".\n"
        f"Confira o código apresentado na troca presencial:\n\n{codigo}\n",
    )


def send_email(message: EmailMessage) -> None:
    """Envia por SMTP; sem MAIL_HOST apenas registra no log. Nunca propaga erro (roda em background)."""
    if not settings.mail_host:
        logger.info("E-mail (MAIL_HOST não configurado)\nPara: %s\nAssunto: %s\n%s",
                    message["To"], message["Subject"], message.get_content())
        return
    try:
        with smtplib.SMTP(settings.mail_host, settings.mail_port, timeout=10) as smtp:
            smtp.starttls()
            if settings.mail_user:
                smtp.login(settings.mail_user, settings.mail_password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        logger.exception("Falha ao enviar e-mail para %s", message["To"])
