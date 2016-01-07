import email
import xml.etree.ElementTree as ET
import os

def a():
    process_directory = './email project/temp_processed'
    if not os.path.exists(process_directory):
        os.makedirs(process_directory)

    tree = ET.parse('./email project/asimov/email_new/from_ben.xml')
    root = tree.getroot()
    for messageNode in root.iter('message'):
        print messageNode.attrib
        file_name = messageNode.attrib['id'] + '.txt'
        with open(os.path.join(process_directory, file_name), "w") as text_file:
            text_file.write(messageNode.find('text').text.encode('utf8'))

  #b = email.message_from_string(a)
  #if b.is_multipart():
  #    for payload in b.get_payload():
  #        # if payload.is_multipart(): ...
  #        print payload.get_payload()
  #else:
  #    print b.get_payload()

if __name__ == '__main__':
    a()
