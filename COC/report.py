from COC.utils import verify_chain

def court_report(evidence):
    logs = evidence.custodylog_set.order_by('timestamp')

    return {
        "Evidence ID": evidence.evidence_id,
        "Case Number": evidence.case_number,
        "Original Hash": evidence.original_hash,
        "Chain Verified": verify_chain(evidence),
        "Total Actions": logs.count(),
        "Custody Logs": [
            {
                "Action": log.action,
                "Performed By": log.performed_by,
                "Role": log.role,
                "Time": log.timestamp,
                "Hash": log.current_hash
            }
            for log in logs
        ]
    }
