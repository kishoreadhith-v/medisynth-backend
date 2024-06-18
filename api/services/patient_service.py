import fitz  # PyMuPDF
import pymongo
import os
from services.gemini_service import extract_patient_info_and_anomalies

# MongoDB setup
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["medisynth"]
patients_collection = db["patients"]

def extract_text_from_pdf(pdf_file):
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in document:
        text += page.get_text()
    return text

def process_lab_report(patient_id, lab_report):
    text = extract_text_from_pdf(lab_report)
    patient_info, anomalies = extract_patient_info_and_anomalies(text)
    
    # Update patient record in MongoDB
    update_result = patients_collection.update_one(
        {"patient_id": patient_id},
        {
            "$set": patient_info,
            "$push": {
                "lab_reports": {
                    "report_id": lab_report.filename,
                    "lab_report_text": text,
                    "anomalies": anomalies
                }
            }
        },
        upsert=True
    )

    return {
        "patient_info_update": update_result.raw_result,
        "anomalies": anomalies
    }
