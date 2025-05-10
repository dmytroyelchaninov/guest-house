import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def send_reservation_emails(reservation):
    """
    Sends a confirmation email to the guest and a notification 
    to the hotel owner, including full reservation details.
    """

    if not reservation.email:
        return

    # --- Context for email templates ---------------------------
    ctx = {
        'reservation': reservation,
        'payment_method': reservation.payment_method.replace('_', ' ').title(),
    }

    # --- Guest confirmation -----------------------------------
    subject_guest = f"Your Guest House Booking #{reservation.id} is Confirmed!"
    from_email   = settings.DEFAULT_FROM_EMAIL
    to_guest     = [reservation.email]

    text_body = render_to_string("emails/booking_confirmation.txt", ctx)
    html_body = render_to_string("emails/booking_confirmation.html", ctx)

    email = EmailMultiAlternatives(subject_guest, text_body, from_email, to_guest)
    email.attach_alternative(html_body, "text/html")
    try:
        email.send(fail_silently=False)
        logger.info("Sent guest confirmation email to %s", reservation.email)
    except Exception as e:
        logger.error("Failed to send guest email to %s: %s", reservation.email, e)

    # --- Owner notification -----------------------------------
    subject_owner = f"[Owner] New Booking #{reservation.id}"
    to_owner      = [settings.DEFAULT_FROM_EMAIL]  # or settings.OWNER_EMAIL

    text_body_o = render_to_string("emails/owner_notification.txt", ctx)
    html_body_o = render_to_string("emails/owner_notification.html", ctx)

    email_o = EmailMultiAlternatives(subject_owner, text_body_o, from_email, to_owner)
    email_o.attach_alternative(html_body_o, "text/html")
    try:
        email_o.send(fail_silently=False)
        logger.info("Sent owner notification for reservation %s", reservation.id)
    except Exception as e:
        logger.error("Failed to send owner email for reservation %s: %s", reservation.id, e)

def send_cancellation_emails(reservation):
    """
    Sends a cancellation notice to the guest and the owner, with full details.
    """
    ctx = {
        'reservation': reservation,
        'payment_method': reservation.payment_method.replace('_',' ').title(),
    }

    # --- Guest cancellation -----------------------------------
    if reservation.email:
        subject = f"Your Booking #{reservation.id} Has Been Cancelled"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_guest   = [reservation.email]

        text_body = render_to_string("emails/cancellation_confirmation.txt", ctx)
        html_body = render_to_string("emails/cancellation_confirmation.html", ctx)

        email = EmailMultiAlternatives(subject, text_body, from_email, to_guest)
        email.attach_alternative(html_body, "text/html")
        try:
            email.send(fail_silently=False)
            logger.info("Sent guest cancellation email to %s", reservation.email)
        except Exception as e:
            logger.error("Failed to send guest cancellation email to %s: %s", reservation.email, e)

    # --- Owner notification ------------------------------------
    subject_o = f"[Owner] Booking #{reservation.id} Cancelled"
    to_owner  = [settings.DEFAULT_FROM_EMAIL]  # or OWNER_EMAIL

    text_body_o = render_to_string("emails/owner_cancellation_notification.txt", ctx)
    html_body_o = render_to_string("emails/owner_cancellation_notification.html", ctx)

    email_o = EmailMultiAlternatives(subject_o, text_body_o, settings.DEFAULT_FROM_EMAIL, to_owner)
    email_o.attach_alternative(html_body_o, "text/html")
    try:
        email_o.send(fail_silently=False)
        logger.info("Sent owner cancellation notice for reservation %s", reservation.id)
    except Exception as e:
        logger.error("Failed to send owner cancellation email for reservation %s: %s", reservation.id, e)

        