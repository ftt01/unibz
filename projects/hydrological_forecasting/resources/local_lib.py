import datetime as dt
import json
import logging
import subprocess
import pytz
import pandas as pd
import glob
from time import sleep

def mkNestedDir(dirTree):
    from os import makedirs
    makedirs(dirTree, exist_ok=True)

def send_email(
    subject, body, receiver_email=["dallatorre.daniele@gmail.com"],
    html=None, attachments=None, 
    cc_receiver_email=None, 
    sender_email = "aiaqua.bz@virgilio.it", password = "AiAqua2@virgilio"):

    import mimetypes
    import smtplib
    import ssl

    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.mime.audio import MIMEAudio

    msg_alternative = MIMEMultipart('alternative')
    
    if body != None:
        part1 = MIMEText(body, "plain")
        msg_alternative.attach(part1)

    if html != None:
        part2 = MIMEText(html, "html")
        msg_alternative.attach(part2)

    msg_mixed = MIMEMultipart('related')
    msg_mixed.attach(msg_alternative)

    if attachments != None:

        for attachment in attachments:
            ctype, encoding = mimetypes.guess_type(attachment[0])
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)

            if maintype == "text":
                fp = open(attachment[0])
                # Note: we should handle calculating the charset
                att = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == "image":
                fp = open(attachment[0], "rb")
                att = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == "audio":
                fp = open(attachment[0], "rb")
                att = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(attachment[0], "rb")
                att= MIMEBase(maintype, subtype)
                att.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(att)
            att.add_header("Content-Disposition", "attachment", filename=attachment[1])
            msg_mixed.attach(att)

    msg_mixed['From'] = sender_email
    msg_mixed['To'] = ', '.join(receiver_email)
    msg_mixed['Subject'] = subject
    if cc_receiver_email != None:
        msg_mixed["Cc"] = ', '.join(cc_receiver_email)

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("out.virgilio.it", 465, context=context) as server:
            server.login(sender_email, password)
            # server.sendmail(sender_email,receiver_email,msg_mixed.as_string())
            server.send_message(msg_mixed)
            server.quit()
    except:
        sleep(10)
        with smtplib.SMTP_SSL("out.virgilio.it", 465, context=context) as server:
            server.login(sender_email, password)
            # server.sendmail(sender_email,receiver_email,msg_mixed.as_string())
            server.send_message(msg_mixed)
            server.quit()


def send_aiaqua_email( attachments, alperia=False ):

    if alperia == True:
        receiver_email=[
            'Giorgio.Battisti@alperia.eu', 
            'Francesco.Turri@alperia.eu', 
            'Andrea.Ropele@alperia.eu',
            'rossella.luchi@hydrodata.it',
            'Matteo.Bartolini@alperia.eu']
        cc_receiver_email=[
            'dallatorre.daniele@gmail.com',
            'ariele.zanfei@unibz.it',
            'andrea.menapace@unibz.it',
            'alberto.deluca@adl.cloud']
    else:
        receiver_email=['dallatorre.daniele@gmail.com']
        cc_receiver_email=None

    send_email(
        # subject="ERRATA CORRIGE | Forecasting Plan | Previsione per il giorno {date}".format( date=(dt.datetime.today() + dt.timedelta(days=1)).strftime('%Y-%m-%d') ),
        subject="Forecasting Plan | Previsione per il giorno {date}".format( date=(dt.datetime.today() + dt.timedelta(days=1)).strftime('%Y-%m-%d') ),
        body="""\
            Fornitura temporanea delle previsioni di portata per il bacino di Plan.
            Email generata in automatico, prego non rispondere.

            ----------------------------------------------------------------
            AIAQUA S.r.l
            Via Volta 13/A
            39100 Bolzano (Italy)
            Phone: +39 3472515613
            E-mail: aiaqua.bz@gmail.com
            PEC: aiaqua@pec.it

            Website: www.AIAQUA.tech

            According to the Regulation EU 2016/679, you are hereby informed that this message contains confidential information that is intended only for the use of the addressee. If you are not the addressee, and have received this message by mistake, please delete it and immediately notify us. In any case you may not copy or disseminate this message to anyone. Thank you.
            Ai sensi del Regolamento UE 679/2016 si precisa che le informazioni contenute in questo messaggio sono riservate ed a uso esclusivo del destinatario. Qualora il messaggio in parola Le fosse pervenuto per errore, La invitiamo ad eliminarlo senza copiarlo e a non inoltrarlo a terzi, dandocene gentilmente comunicazione. Grazie.
            Im Sinne der Datenschutzgrundverordnung (DSGV n. 679/2016) informieren wir Sie, dass die in dieser E-Mail enthaltenen Informationen vertraulich und ausschließlich für den Adressaten bestimmt sind. Sollten Sie diese Nachricht irrtümlich erhalten haben, bitten wir Sie, diese zu vernichten ohne sie zu kopieren oder an Dritte weiterzuleiten. Auch bitten wir Sie, uns darüber unverzüglich in Kenntnis zu setzen. Danke.
        """,
        html="""\
            <html>
                <head>
                    <style>
                        body {
                        font-size: 110%;
                        }

                        h1 {
                        font-size: 1.1em;
                        }

                        h2 {
                        font-size: 0.75em;
                        }

                        p {
                        font-size: 1.0em;
                        }

                        p.small {
                        font-style: normal;
                        font-size: 0.75em;
                        }

                        p.italic {
                        font-style: italic;
                        }

                        p.thick {
                        font-weight: bold;
                        }
                    </style>
                </head>
            <body>
                <p class="thick">Fornitura temporanea delle previsioni di portata per il bacino di Plan.</p>

                <p class="italic">Email generata in automatico, prego non rispondere. </p>

                ----------------------------------------------------------------

                <p>AIAQUA S.r.l<br>
                Via Volta 13/A<br>
                39100 Bolzano (Italy)<br>
                Phone: +39 3472515613<br>
                E-mail: <a href="aiaqua.bz@gmail.com">aiaqua.bz@gmail.com</a><br>
                PEC: <a href="aiaqua@pec.it">aiaqua@pec.it</a></p>

                <p>Website: <a href="www.AIAQUA.tech">www.AIAQUA.tech</a></p>

                <p class="small">According to the Regulation EU 2016/679, you are hereby informed that this message contains confidential information that is intended only for the use of the addressee. If you are not the addressee, and have received this message by mistake, please delete it and immediately notify us. In any case you may not copy or disseminate this message to anyone. Thank you.</p>
                <p class="small">Ai sensi del Regolamento UE 679/2016 si precisa che le informazioni contenute in questo messaggio sono riservate ed a uso esclusivo del destinatario. Qualora il messaggio in parola Le fosse pervenuto per errore, La invitiamo ad eliminarlo senza copiarlo e a non inoltrarlo a terzi, dandocene gentilmente comunicazione. Grazie.</p>
                <p class="small">Im Sinne der Datenschutzgrundverordnung (DSGV n. 679/2016) informieren wir Sie, dass die in dieser E-Mail enthaltenen Informationen vertraulich und ausschlie&szlig;lich f&uuml;r den Adressaten bestimmt sind. Sollten Sie diese Nachricht irrt&uuml;mlich erhalten haben, bitten wir Sie, diese zu vernichten ohne sie zu kopieren oder an Dritte weiterzuleiten. Auch bitten wir Sie, uns dar&uuml;ber unverz&uuml;glich in Kenntnis zu setzen. Danke.</p>
            </body></html>
        """,
        attachments=attachments,
        receiver_email=receiver_email, 
        cc_receiver_email=cc_receiver_email, 
        sender_email = "aiaqua.bz@virgilio.it",
        password = "AiAqua2@virgilio"
    )