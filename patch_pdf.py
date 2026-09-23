import re

def make_deterministic(filepath):
    with open(filepath, 'rb') as f:
        pdf_data = f.read()
    
    pdf_data = re.sub(b'/ID\\s*\\[<[0-9a-fA-F]+><[0-9a-fA-F]+>\\]', b'/ID [<00000000000000000000000000000000><00000000000000000000000000000000>]', pdf_data)
    pdf_data = re.sub(b'/CreationDate \\(D:[0-9]{14}[^\\)]*\\)', b'/CreationDate (D:20260923000000Z)', pdf_data)
    pdf_data = re.sub(b'/ModDate \\(D:[0-9]{14}[^\\)]*\\)', b'/ModDate (D:20260923000000Z)', pdf_data)
    
    with open(filepath, 'wb') as f:
        f.write(pdf_data)

if __name__ == '__main__':
    make_deterministic('test1.pdf')
    make_deterministic('test2.pdf')
