from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI()

# Load sample drug data
with open("data/sample_drugs.json", "r") as f:
    drug_data = json.load(f)

# Helper: Find a drug by name
def find_drug_by_name(name: str):
    for drug in drug_data:
        if drug["name"].lower() == name.lower():
            return drug
    return None

# ---------------------- MODELS ----------------------
class DrugList(BaseModel):
    drugs: List[str]

class DrugName(BaseModel):
    name: str

class ConditionName(BaseModel):
    condition: str

# ---------------------- ENDPOINTS ----------------------

# 1. Get full drug information
@app.get("/drug_info")
def get_drug_info(name: str = Query(..., description="Enter the drug name")):
    drug = find_drug_by_name(name)
    if drug:
        return drug
    else:
        raise HTTPException(status_code=404, detail="Drug not found")

# 2. Check for drug interactions
@app.post("/check_interactions")
def check_interactions(drug_list: DrugList):
    found_drugs = [find_drug_by_name(name) for name in drug_list.drugs]
    found_drugs = [d for d in found_drugs if d is not None]

    if len(found_drugs) < 2:
        raise HTTPException(status_code=400, detail="At least two valid known drugs are required")

    interactions = []
    for i in range(len(found_drugs)):
        for j in range(i + 1, len(found_drugs)):
            d1 = found_drugs[i]
            d2 = found_drugs[j]
            if d2["name"] in d1["interactions"] or d1["name"] in d2["interactions"]:
                interactions.append(f"{d1['name']} interacts with {d2['name']}")

    if interactions:
        return {"interactions": interactions}
    else:
        return {"message": "No interactions found"}

# 3. Suggest alternatives
@app.get("/suggest_alternatives")
def suggest_alternatives(name: str):
    drug = find_drug_by_name(name)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    suggestions = drug.get("alternatives", [])
    return {"suggested_alternatives": suggestions}

# 4. Get dosage and duration
@app.get("/dosage_duration")
def get_dosage_duration(name: str):
    drug = find_drug_by_name(name)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {
        "dosage": drug.get("dosage", "Not specified"),
        "duration": drug.get("duration", "Not specified")
    }

# 5. Recommend drugs by condition (supports flexible match)
@app.get("/recommended_by_condition")
def recommended_by_condition(condition: str):
    matched = []
    keywords = [
        condition.lower(),
        "cold", "severe cold", "throat pain", "throat infection", "sore throat",
        "body pain", "severe body pain", "fever", "inflammation", "infection",
        "bacterial infection", "pain", "headache", "flu", "asthma", "high blood pressure",
        "hypertension", "diabetes", "blood sugar", "cholesterol", "acidity", "reflux",
        "gastric", "thyroid", "heart health", "blood thinner", "allergy", "sneezing",
        "stomach pain", "abdominal pain", "cramps", "ibs"
    ]
    for drug in drug_data:
        drug_conditions = drug.get("condition", "").lower()
        if any(keyword in drug_conditions for keyword in keywords):
            matched.append(drug["name"])
    if not matched:
        raise HTTPException(status_code=404, detail="No recommended drugs found for this condition")
    return {"recommended_drugs": matched}

# 6. Identify medicine from image filename (dummy logic)
@app.post("/identify_medicine_image")
def identify_medicine_image(file: UploadFile = File(...)):
    filename = file.filename.lower()
    known_drugs = [
        "paracetamol", "ibuprofen", "aspirin", "amoxicillin", "atorvastatin",
        "metformin", "omeprazole", "losartan", "cetirizine", "pantoprazole",
        "azithromycin", "salbutamol", "lisinopril", "clopidogrel", "levothyroxine",
        "dolo", "mebeverine"
    ]
    for drug in known_drugs:
        if drug in filename:
            return {"identified_drug": drug.capitalize()}
    return {"identified_drug": "Unknown - Image recognition model not implemented yet"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=10000)
