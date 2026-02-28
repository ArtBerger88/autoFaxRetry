import random

#replace later with fax service
def send_fax(pdf_path, fax_number):
    # Temporary fake sender for testing retry logic
    # 30% chance of success
    return random.random() < 0.3