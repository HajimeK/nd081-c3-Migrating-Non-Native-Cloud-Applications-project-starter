import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database
    POSTGRES_URL = os.environ.get('POSTGRES_URL')
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PW = os.environ.get('POSTGRES_PW')
    POSTGRES_DB = os.environ.get('POSTGRES_DB')
    #conn_string = f'dbname=\'{POSTGRES_DB}\' user=\'{POSTGRES_USER}\' host=\'{POSTGRES_URL}\' password=\'{POSTGRES_PW}\' port=\'5432\' sslmode=\'true\''
    conn_string = f'dbname=\'{POSTGRES_DB}\' user=\'{POSTGRES_USER}\' host=\'{POSTGRES_URL}\' password=\'{POSTGRES_PW}\' port=\'5432\''

    conn = psycopg2.connect(conn_string)
    logging.info('after connetion:')
    cursor = conn.cursor()

    try:
        # TODO: Get notification message and subject from database using the notification_id
        cursor.execute(f"SELECT * FROM notification WHERE id = {notification_id};")
        notification = cursor.fetchone()

        # TODO: Get attendees email and name
        cursor.execute("SELECT * FROM attendee;")
        attendees = cursor.fetchall()

        completed_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        status = f'Notified {len(attendees)} attendees'
        cursor.execute(f"UPDATE notification SET status = '{status}', completed_date = '{completed_date}' WHERE id = {notification_id};")

        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            send_email(str(attendee[5]), "{} {} {}".format(str(notification[5]), str(attendee[1]), str(attendee[2])), str(notification[2]))

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        completed_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        status = f'Notified {len(attendees)} attendees'
        cursor.execute(f"UPDATE notification SET status = '{status}', completed_date = '{completed_date}' WHERE id = {notification_id};")
        

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Connection Closed")

def send_email(email, subject, body):
    logging.info(f"Sending email: {subject}")

    adminMail = os.environ.get('MAIL_ADDRESS')
    sendgrid_api_key = os.environ.get('SENDGRID_SECRET__KEY')

    message = Mail(
        from_email = adminMail,
        to_emails = email,
        subject = subject,
        plain_text_content = body)

    sg = SendGridAPIClient(sendgrid_api_key)
    sg.send(message)