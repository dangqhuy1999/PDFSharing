"""
In Windows Computer,
Open the link and Select security,
https://myaccount.google.com/security?utm_source=account-marketing-page&utm_medium=go-to-account-button
Select search,
Type and Select app Password , You will be asked to Sign in with your Account Password to continue to Create or delete app Password,
https://photos.app.goo.gl/4dAUgeiP2AvukCYP9
Or, Open the link , Sign in and follow the instructions,
https://myaccount.google.com/apppasswords
https://notifications.google.com/g/p/ANia

# https://youtu.be/K21BSZPFIjQ
Extract selected mails from your gmail account

1. Make sure you enable IMAP in your gmail settings
(Log on to your Gmail account and go to Settings, See All Settings, and select
 Forwarding and POP/IMAP tab. In the "IMAP access" section, select Enable IMAP.)

2. If you have 2-factor authentication, gmail requires you to create an application
specific password that you need to use. 
Go to your Google account settings and click on 'Security'.
Scroll down to App Passwords under 2 step verification.
Select Mail under Select App. and Other under Select Device. (Give a name, e.g., python)
The system gives you a password that you need to use to authenticate from python.
"""

# Importing libraries
import imaplib
import email
from email.header import decode_header
from time import sleep
import yaml
import main


with open("credentials.yml") as f:
    content = f.read()
    
# from credentials.yml import user name and password
my_credentials = yaml.load(content, Loader=yaml.FullLoader)

#Load the user name and passwd from yaml file
user, password = my_credentials["user"], my_credentials["password"]

#URL for IMAP connection
imap_url = 'imap.gmail.com'

# Connection with GMAIL using SSL
mail = imaplib.IMAP4_SSL(imap_url)

# Log in using your credentials
mail.login(user, password)
n=input('login thanh cong!! ')
processed_times = set()
while True:
    # Select the Inbox to fetch messages
    mail.select('Inbox')
    # Tìm kiếm tất cả email chưa đọc
    status, messages = mail.search(None, 'UNSEEN')  # Tìm thư chưa đọc
    if status == "OK":
        email_ids = messages[0].split()
        count = len(email_ids)  # Đếm số lượng email chưa đọc
        print(f'Mail chua doc: {count}')
        if count == 0:
                print("Không có email chưa đọc.")
        else: 
            email_ids.reverse()
            print(f"Số lượng email chưa đọc: {count}")
            endparty = 0
            for num in email_ids:
                endparty +=1
                if endparty > 5:
                  break
                # Lấy thông tin thư
                status, msg_data = mail.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                # Giải mã tiêu đề
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')

                # Lấy thông tin người gửi
                from_ = msg.get("From")

                # Lấy thời gian nhận
                date_received = msg.get("Date")
                print(date_received)
                
                date_received_parsed = email.utils.parsedate_to_datetime(date_received)
                if date_received_parsed in processed_times:
                  continue
                # Lấy nội dung email
                body = ""
                attachments = []
                if msg.is_multipart():
                    count = sum(1 for _ in msg.walk())
                    #n=input(f"Số phần tử trong email: {count}")
                    
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        #n=input(content_disposition)
                        #if content_type == "text/html":
                        #    print('HIHI')
                        #    body = part.get_payload(decode=True).decode()
                        #   print(body)
                        # Kiểm tra nếu phần này là một tệp đính kèm
                        if "attachment" in content_disposition or "inline" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                # Kiểm tra xem tệp có phải là PDF, ảnh hoặc HTML không
                                #if content_type == 'application/pdf' or content_type.startswith('image/') or content_type == 'audio/mpeg':
                                if content_type == 'application/pdf':
                                    attachments.append(filename)
                                    # Lưu tệp đính kèm vào thư mục hiện tại
                                    with open(filename, 'wb') as f:
                                        f.write(part.get_payload(decode=True))
                                    #In thông tin thư
                                    print(f"Thư mới từ: {from_}")
                                    print(f"Tiêu đề: {subject}")
                                    print(f"Thời gian nhận: {date_received}")
                                    print(filename)
                                    n=input("đợi tí")
                                    #print(f"Nội dung HTML:\n{body}")
                                    print("-" * 50)
                                    json_file = main.getDataPDF(filename)
                                    main.processPDF(json_file)
                                    print("Hê Hê!!!")
                else:
                    # Nếu không phải multipart, lấy payload
                    print('HIHo')
                    #body = msg.get_payload(decode=True).decode()
                # In danh sách các tệp đính kèm đã tải về
                if attachments:
                    print("Các tệp đính kèm đã được lưu:", attachments)

                
                with open ('mail_log.txt', 'a', encoding='utf-8') as file:
                    file.write(f"From: {from_}\nSubject: {subject}\nData_received:{date_received}\n{date_received_parsed}\n\n\n")
                    file.write(body)
                processed_times.add(date_received_parsed)
                #Check SEEN
                mail.store(num, '+FLAGS', '\\Seen')
                #n=input('toinua')
    sleep(5)