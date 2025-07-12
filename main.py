from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

# Load sample drug data
with open("data/sample_drugs.json", "r") as f:
    drug_data = json.load(f)

# Helper: Find a drug by name or alias
def find_drug_by_name(name: str):
    name = name.strip().lower()
    for drug in drug_data:
        if name == drug["name"].lower():
            return drug
        if "aliases" in drug:
            for alias in drug["aliases"]:
                if name == alias.lower():
                    return drug
    return None

# ---------------------- MODELS ----------------------
class DrugList(BaseModel):
    drugs: List[str]

# ---------------------- ENDPOINTS ----------------------

@app.get("/")
def root():
    return {"message": "API is working!"}

# 1. Get full drug information
@app.get("/get_drug_info")
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
            if d2["name"] in d1.get("interactions", []) or d1["name"] in d2.get("interactions", []):
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

# 5. Recommend drugs by condition
@app.get("/recommended_by_condition")
def recommended_by_condition(condition: str):
    condition = condition.lower()
    matched = []
    for drug in drug_data:
        if condition in drug.get("used_for", "").lower():
            matched.append(drug["name"])
    if not matched:
        raise HTTPException(status_code=404, detail="No recommended drugs found for this condition")
    return {"recommended_drugs": matched}

# 6. Identify medicine by image filename (dummy logic using 200 drugs)
@app.post("/identify_medicine_image")
def identify_medicine_image(file: UploadFile = File(...)):
    filename = file.filename.lower()
    known_drugs = [
        "calcitriol", "humalog", "candid", "honitus", "sitagliptin", "permite", "atorvastatin",
        "empagliflozin", "insulin lispro", "acetaminophen", "norfloxacin", "phenergan", "moov", "cetaphil",
        "metoprolol", "neurobion forte", "volini", "cyclopam", "cough syrup", "zandu balm", "torex",
        "methylcobalamin", "grilinctus", "buscopan", "omeprazole", "cetirizine", "sporlac", "zincovit",
        "theophylline", "rosuvastatin", "paracetamol", "dolo 650", "digene", "calpol", "crocin", "aspirin",
        "pantoprazole", "rantac", "domperidone", "meftal spas", "allegra", "metformin", "losartan",
        "levocetirizine", "diclofenac", "ciprofloxacin", "ondansetron", "telmisartan", "benadryl", "t-minic",
        "combiflam", "becosules", "loperamide", "electral", "ecosprin", "montair lc", "sinarest", "loratadine",
        "amoxicillin", "azithromycin", "dexamethasone", "fluconazole", "neosporin", "hydrocortisone", "vitamin c",
        "iron", "calcium", "b-complex", "folic acid", "rabeprazole", "esomeprazole", "lansoprazole", "sucralfate",
        "tramadol", "codeine", "salbutamol", "montelukast", "levofloxacin", "moxifloxacin", "tetracycline",
        "doxycycline", "clarithromycin", "ketoconazole", "terbinafine", "itraconazole", "olmesartan", "amlodipine",
        "propranolol", "atenolol", "spironolactone", "furosemide", "lisinopril", "enalapril", "ramipril",
        "simvastatin", "fenofibrate", "gemfibrozil", "glimepiride", "gliclazide", "pioglitazone", "vildagliptin",
        "linagliptin", "canagliflozin", "dapagliflozin", "insulin glargine", "insulin aspart", "novorapid",
        "humulin", "vicks", "relent", "ascoril", "tusq", "koflet", "seven seas", "liv 52", "omez", "gaviscon",
        "anaspas", "mebeverine", "zantac", "perinorm", "motilium", "emeset", "vomikind", "vomidon", "vomistop",
        "nasivion", "otrivin", "xylometazoline", "avil", "tavegyl", "azee", "taxim", "monocef", "cefixime",
        "cefpodoxime", "augmentin", "clavam", "flagyl", "tinidazole", "nitrofurantoin", "bactrim", "septran",
        "uribid", "citralka", "alkasol", "spasmo-proxyvon", "iodex", "sensodyne", "colgate", "listerine",
        "dettol", "savlon", "betnovate", "lulifin", "onabet", "surfaz", "dermocalm", "clocip", "itch guard",
        "ring guard", "scaboma"
    ]
    for drug in known_drugs:
        if drug in filename:
            return {"identified_drug": drug.capitalize()}
    return {"identified_drug": "Unknown - Image recognition model not implemented yet"}
