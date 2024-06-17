import pymongo

# MongoDB setup
client = pymongo.MongoClient("your_mongo_connection_string")
db = client["medisynth"]
patients_collection = db["patients"]

def detect_anomalies(patient_id, report_id):
    patient = patients_collection.find_one({"patient_id": patient_id, "lab_reports.report_id": report_id})
    if not patient:
        return {"error": "Report not found"}

    for report in patient.get("lab_reports", []):
        if report["report_id"] == report_id:
            return report.get("anomalies", [])

    return {"error": "Anomalies not found"}
