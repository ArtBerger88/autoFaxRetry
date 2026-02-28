from retry_engine import send_with_retry

if __name__ == "__main__":
    pdf = "data/sample.pdf"
    fax = "5551234567"
    send_with_retry(pdf, fax, max_attempts=10, delay_seconds=30)