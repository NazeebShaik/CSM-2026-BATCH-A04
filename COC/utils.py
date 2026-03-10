import hashlib

def verify_chain(evidence):
    logs = evidence.custodylog_set.order_by('timestamp')
    prev = None

    for log in logs:
        raw = f"{evidence.evidence_id}{log.action}{log.performed_by}{log.timestamp}{prev}"
        expected = hashlib.sha256(raw.encode()).hexdigest()
        if log.current_hash != expected:
            return False
        prev = log.current_hash

    return True
