class LabReport:
    def __init__(self, report_id, patient_id, collected_at, reported_at, data):
        self.report_id = report_id
        self.patient_id = patient_id
        self.collected_at = collected_at
        self.reported_at = reported_at
        self.data = data

    def to_dict(self):
        return {
            "report_id": self.report_id,
            "patient_id": self.patient_id,
            "collected_at": self.collected_at,
            "reported_at": self.reported_at,
            "data": self.data
        }
