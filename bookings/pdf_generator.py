"""
PDF Confirmation Generator — Al Andalus Hotel
Generates a professional booking confirmation PDF using ReportLab.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from io import BytesIO
import datetime


# ── BRAND COLORS ──────────────────────────────────────
GOLD    = colors.HexColor('#C9A96E')
DARK    = colors.HexColor('#1A1D27')
DARK2   = colors.HexColor('#2C2C2C')
WHITE   = colors.white
LIGHT   = colors.HexColor('#F9F7F3')
GRAY    = colors.HexColor('#6B7280')
GREEN   = colors.HexColor('#10B981')
BORDER  = colors.HexColor('#E5E7EB')


def generate_booking_pdf(booking, site_url='http://127.0.0.1:8000', info=None):
    """
    Generate a booking confirmation PDF.
    Returns a BytesIO buffer containing the PDF.
    """
    # Fetch hotel info from database
    if info is None:
        try:
            from content.models import HotelInfo
            from content.models import HotelRules
            info = HotelInfo.objects.first()
            rules = HotelRules.get_instance()
        except Exception:
            info = None
            rules = None
    else:
        try:
            from content.models import HotelRules
            rules = HotelRules.get_instance()
        except Exception:
            rules = None

    # Dynamic values from info/rules (with fallbacks)
    hotel_name     = info.hotel_name    if info else "Al Andalus"
    hotel_address  = info.address       if info else "Boulevard de la Corniche, Casablanca, Maroc"
    hotel_stars    = "★" * (info.stars  if info else 5)
    checkin_time   = info.checkin_time  if info else "14h00"
    checkout_time  = info.checkout_time if info else "12h00"
    hotel_phone    = info.phone         if info else "+212 5 22 XX XX XX"
    hotel_email    = info.email         if info else "contact@hotel.ma"
    cancellation   = rules.cancellation_policy[:80] + "..." if rules and rules.cancellation_policy else "Annulation gratuite 48h avant l'arrivée"

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm,
        title=f"Confirmation Réservation #AL{booking.id:05d}",
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── HEADER ────────────────────────────────────────
    # Gold top bar
    header_data = [['']]
    header_tbl = Table(header_data, colWidths=[17*cm], rowHeights=[0.5*cm])
    header_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GOLD),
        ('LINEABOVE',  (0,0), (-1,-1), 0, GOLD),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 0.4*cm))

    # Hotel name + stars
    hotel_name_style = ParagraphStyle(
        'HotelName', fontSize=26, textColor=DARK,
        fontName='Helvetica-Bold', alignment=TA_CENTER, leading=28,
    )
    stars_style = ParagraphStyle(
        'Stars', fontSize=11, textColor=GOLD,
        fontName='Helvetica', alignment=TA_CENTER,
    )
    tagline_style = ParagraphStyle(
        'Tagline', fontSize=8, textColor=GRAY,
        fontName='Helvetica', alignment=TA_CENTER, leading=12,
        spaceBefore=2,
    )

    story.append(Paragraph(hotel_name, hotel_name_style))
    story.append(Paragraph(" ".join(list(hotel_stars)), stars_style))
    story.append(Paragraph(f"{(info.tagline if info else "HÔTEL & SPA").upper()}", tagline_style))
    story.append(Spacer(1, 0.4*cm))

    # Gold divider
    story.append(HRFlowable(width='100%', thickness=1.5, color=GOLD, spaceAfter=0.5*cm))

    # ── CONFIRMATION BANNER ───────────────────────────
    banner_data = [['✓  RÉSERVATION CONFIRMÉE']]
    banner_tbl = Table(banner_data, colWidths=[17*cm], rowHeights=[1.1*cm])
    banner_tbl.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,-1), GOLD),
        ('TEXTCOLOR',   (0,0), (-1,-1), WHITE),
        ('FONTNAME',    (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 14),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('ROUNDEDCORNERS', (0,0), (-1,-1), [4,4,4,4]),
    ]))
    story.append(banner_tbl)
    story.append(Spacer(1, 0.5*cm))

    # Reference number
    ref_style = ParagraphStyle(
        'Ref', fontSize=11, textColor=GRAY,
        fontName='Helvetica', alignment=TA_CENTER,
    )
    ref_num_style = ParagraphStyle(
        'RefNum', fontSize=20, textColor=DARK,
        fontName='Helvetica-Bold', alignment=TA_CENTER,
    )
    story.append(Paragraph("Numéro de réservation", ref_style))
    story.append(Paragraph(f"#AL{booking.id:05d}", ref_num_style))
    story.append(Spacer(1, 0.5*cm))

    # ── CLIENT INFO ───────────────────────────────────
    section_style = ParagraphStyle(
        'Section', fontSize=9, textColor=GOLD,
        fontName='Helvetica-Bold', alignment=TA_LEFT,
        textTransform='uppercase', spaceAfter=0.2*cm,
    )
    story.append(Paragraph("▸ Informations du client", section_style))

    client_data = [
        ['Nom', booking.name],
        ['Email', booking.email],
        ['Téléphone', booking.phone or '—'],
    ]
    client_tbl = Table(client_data, colWidths=[4*cm, 13*cm])
    client_tbl.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), GRAY),
        ('TEXTCOLOR', (1,0), (1,-1), DARK),
        ('TOPPADDING',(0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, BORDER),
        ('BACKGROUND',(0,0), (-1,-1), LIGHT),
        ('ROUNDEDCORNERS',(0,0),(-1,-1),[4,4,4,4]),
    ]))
    story.append(client_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── BOOKING DETAILS ───────────────────────────────
    story.append(Paragraph("▸ Détails du séjour", section_style))

    nights = (booking.check_out - booking.check_in).days

    # Format dates in French
    MONTHS_FR = ['', 'janvier','février','mars','avril','mai','juin',
                 'juillet','août','septembre','octobre','novembre','décembre']
    DAYS_FR   = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']

    def fmt_date(d):
        day_name = DAYS_FR[d.weekday()]
        return f"{day_name} {d.day} {MONTHS_FR[d.month]} {d.year}"

    details_data = [
        ['Chambre',        booking.room.name],
        ['Catégorie',      booking.room.get_category_display()],
        [f'Arrivée',        fmt_date(booking.check_in) + f'  (Check-in à partir de {checkin_time})'],
        [f'Départ',         fmt_date(booking.check_out) + f'  (Check-out avant {checkout_time})'],
        ['Durée',          f"{nights} nuit{'s' if nights > 1 else ''}"],
        ['Voyageurs',      f"{booking.guests} personne{'s' if booking.guests > 1 else ''}"],
    ]
    if booking.special_requests:
        details_data.append(['Demandes spéc.', booking.special_requests])

    details_tbl = Table(details_data, colWidths=[4*cm, 13*cm])
    details_tbl.setStyle(TableStyle([
        ('FONTNAME',    (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',    (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('TEXTCOLOR',   (0,0), (0,-1), GRAY),
        ('TEXTCOLOR',   (1,0), (1,-1), DARK),
        ('TOPPADDING',  (0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('LINEBELOW',   (0,0), (-1,-2), 0.5, BORDER),
        ('BACKGROUND',  (0,0), (-1,-1), LIGHT),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT, WHITE]),
    ]))
    story.append(details_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── PAYMENT SUMMARY ───────────────────────────────
    story.append(Paragraph("▸ Récapitulatif du paiement", section_style))

    price_per_night = float(booking.room.price)
    total = float(booking.total_price)

    payment_data = [
        [f"{booking.room.name}", f"{price_per_night:,.0f} MAD/nuit"],
        [f"{nights} nuit{'s' if nights > 1 else ''} × {price_per_night:,.0f} MAD", f"{total:,.0f} MAD"],
    ]

    # Check payment status
    try:
        payment = booking.payment
        status_txt  = payment.get_status_display()
        method_txt  = payment.get_method_display()
        if payment.card_last4:
            method_txt += f" •••• {payment.card_last4}"
        payment_data.append(['Méthode', method_txt])
        payment_data.append(['Statut paiement', status_txt])
        if payment.transaction_id:
            payment_data.append(['Réf. transaction', payment.transaction_id])
    except Exception:
        payment_data.append(['Paiement', 'À régler sur place à l\'arrivée'])

    # Total row
    total_row = [['MONTANT TOTAL', f"{total:,.0f} MAD"]]
    total_tbl = Table(total_row, colWidths=[13*cm, 4*cm])
    total_tbl.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,-1), GOLD),
        ('TEXTCOLOR',   (0,0), (-1,-1), WHITE),
        ('FONTNAME',    (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 12),
        ('ALIGN',       (1,0), (1,-1), 'RIGHT'),
        ('TOPPADDING',  (0,0),(-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
        ('LEFTPADDING', (0,0),(0,-1), 10),
        ('RIGHTPADDING',(1,0),(1,-1), 10),
    ]))

    pay_tbl = Table(payment_data, colWidths=[10*cm, 7*cm])
    pay_tbl.setStyle(TableStyle([
        ('FONTNAME',    (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',    (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('TEXTCOLOR',   (0,0), (0,-1), GRAY),
        ('TEXTCOLOR',   (1,0), (1,-1), DARK),
        ('ALIGN',       (1,0), (1,-1), 'RIGHT'),
        ('TOPPADDING',  (0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('LINEBELOW',   (0,0), (-1,-2), 0.5, BORDER),
        ('BACKGROUND',  (0,0), (-1,-1), LIGHT),
    ]))
    story.append(pay_tbl)
    story.append(Spacer(1, 0.2*cm))
    story.append(total_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── INCLUSIONS ────────────────────────────────────
    inclusions = []
    room = booking.room
    if room.includes_breakfast:  inclusions.append("✓  Petit-déjeuner continental inclus")
    if room.includes_parking:    inclusions.append("✓  Parking gratuit — 1 place sécurisée")
    if room.free_cancellation:   inclusions.append("✓  Annulation gratuite jusqu'à 48h avant l'arrivée")
    if room.no_prepayment:       inclusions.append("✓  Aucun prépaiement requis — payez sur place")

    if inclusions:
        incl_items = [[inc] for inc in inclusions]
        incl_tbl = Table(incl_items, colWidths=[17*cm])
        incl_tbl.setStyle(TableStyle([
            ('FONTNAME',    (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE',    (0,0), (-1,-1), 9),
            ('TEXTCOLOR',   (0,0), (-1,-1), colors.HexColor('#065F46')),
            ('BACKGROUND',  (0,0), (-1,-1), colors.HexColor('#F0FFF4')),
            ('LINEBELOW',   (0,0), (-1,-2), 0.3, BORDER),
            ('TOPPADDING',  (0,0),(-1,-1), 5),
            ('BOTTOMPADDING',(0,0),(-1,-1), 5),
            ('LEFTPADDING', (0,0),(-1,-1), 12),
        ]))
        story.append(incl_tbl)
        story.append(Spacer(1, 0.5*cm))

    # ── QR CODE + IMPORTANT INFO ──────────────────────
    # QR Code pointing to booking confirmation URL
    qr_url = f"{site_url}/reservations/confirmation/{booking.id}/"
    try:
        qr = QrCodeWidget(qr_url)
        d   = Drawing(2.2*cm, 2.2*cm)
        d.add(qr)
        # Scale the QR code
        qr_bounds = qr.getBounds()
        qr_w = qr_bounds[2] - qr_bounds[0]
        qr_h = qr_bounds[3] - qr_bounds[1]
        d.width  = 2.2*cm
        d.height = 2.2*cm
        d.transform = (2.2*cm/qr_w, 0, 0, 2.2*cm/qr_h, -qr_bounds[0]*2.2*cm/qr_w, -qr_bounds[1]*2.2*cm/qr_h)

        qr_txt_style = ParagraphStyle(
            'QRtxt', fontSize=7, textColor=GRAY,
            fontName='Helvetica', alignment=TA_CENTER,
        )
        qr_data = [[d, Paragraph(
            f"<b>Réf.</b> #AL{booking.id:05d}<br/>Scannez pour accéder<br/>à votre réservation",
            qr_txt_style
        )]]
        qr_tbl = Table(qr_data, colWidths=[2.8*cm, 14.2*cm])
        qr_tbl.setStyle(TableStyle([
            ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
            ('LEFTPADDING',(0,0),(0,-1), 5),
        ]))
        story.append(qr_tbl)
    except Exception:
        pass  # Skip QR if fails

    story.append(Spacer(1, 0.4*cm))

    # ── INFO BOX ──────────────────────────────────────
    info_title_style = ParagraphStyle(
        'InfoTitle', fontSize=9, textColor=colors.HexColor('#92400E'),
        fontName='Helvetica-Bold', alignment=TA_LEFT,
    )
    info_body_style = ParagraphStyle(
        'InfoBody', fontSize=8, textColor=colors.HexColor('#78350F'),
        fontName='Helvetica', alignment=TA_LEFT, leading=14,
    )
    info_data = [[
        Paragraph("ℹ️  Informations importantes", info_title_style),
    ],[
        Paragraph(
            f"<b>• La présentation de cette confirmation est requise à l'arrivée.</b><br/>"
            f"• Pièce d'identité requise à la réception lors de l'enregistrement<br/>"
            f"• Check-in à partir de <b>{checkin_time}</b> · Check-out avant <b>{checkout_time}</b><br/>"
            f"• En cas d'arrivée tardive, veuillez prévenir la réception au {hotel_phone}<br/>"
            f"• Ce document fait office de confirmation officielle de réservation",
            info_body_style
        ),
    ]]
    info_tbl = Table(info_data, colWidths=[17*cm])
    info_tbl.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,-1), colors.HexColor('#FEF3C7')),
        ('LINEABOVE',   (0,0), (-1,0),  1, colors.HexColor('#FCD34D')),
        ('LINEBELOW',   (0,-1),(-1,-1), 1, colors.HexColor('#FCD34D')),
        ('TOPPADDING',  (0,0),(-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
        ('LEFTPADDING', (0,0),(-1,-1), 12),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 0.4*cm))

    # ── FOOTER ────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1, color=GOLD, spaceBefore=0.2*cm))
    footer_style = ParagraphStyle(
        'Footer', fontSize=8, textColor=GRAY,
        fontName='Helvetica', alignment=TA_CENTER, leading=14,
    )
    story.append(Paragraph(
        f"<b>{hotel_name} {hotel_stars}</b> · {hotel_address}<br/>"
        f"Document généré le {datetime.date.today().strftime('%d/%m/%Y')} · "
        f"Réservation #AL{booking.id:05d} · Ce document est votre confirmation officielle",
        footer_style
    ))

    # ── GOLD BOTTOM BAR ───────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    bottom_data = [['']]
    bottom_tbl = Table(bottom_data, colWidths=[17*cm], rowHeights=[0.4*cm])
    bottom_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GOLD),
    ]))
    story.append(bottom_tbl)

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
