from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# ✅ MATCH your actual folder name here
MODEL_PATH = "emotion_model/distilbert_model_go_emotions_dataset"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True)

id2label = {
    0: "angry",
    1: "bad",
    2: "fearful",
    3: "happy",
    4: "neutral",
    5: "sad",
    6: "surprised"
}

def predict(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()
    return id2label.get(predicted_class, "unknown")
