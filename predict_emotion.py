import torch
from transformers import AutoTokenizer, AutoModel
import torch.nn as nn
import os
from safetensors.torch import load_file as safe_load

# 1. Define emotion columns
emotion_columns = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion", "curiosity",
    "desire", "disappointment", "disapproval", "disgust", "embarrassment", "excitement", "fear",
    "gratitude", "grief", "joy", "love", "nervousness", "optimism", "pride", "realization", "relief",
    "remorse", "sadness", "surprise", "neutral"
]

# 2. Define the model class (copy from your training code)
class EmotionClassifier(nn.Module):
    def __init__(self, model_name="roberta-base", num_labels=28):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_labels)
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0]
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return logits

# 3. Load tokenizer and model
model_dir = "emotion_model_roberta_final"
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = EmotionClassifier(num_labels=len(emotion_columns))
model.load_state_dict(safe_load(os.path.join(model_dir, "emotion_classifier.safetensors")))
model.eval()

# 4. Prediction function
def predict(text):
    inputs = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=128,
        return_tensors="pt"
    )
    with torch.no_grad():
        logits = model(inputs["input_ids"], inputs["attention_mask"])
        probs = torch.sigmoid(logits).squeeze().cpu().numpy()
    # Get top emotions (you can adjust threshold or top-k)
    threshold = 0.5
    predicted = [emotion_columns[i] for i, p in enumerate(probs) if p > threshold]
    return predicted if predicted else ["neutral"]