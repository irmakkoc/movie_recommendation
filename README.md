# 🎬 Sentiment-Based Movie Recommendation System

This project is a graduation thesis that combines Natural Language Processing with a movie recommendation engine. It analyzes users’ emotional input using a custom fine-tuned RoBERTa model and recommends movies that best match their mood.

## 🧠 Project Overview

The goal of this project is to build an emotionally intelligent movie recommendation system. Users express their current feelings in natural language, and the system responds with movie suggestions that align with their emotional state.

### ✅ Key Features

- 🧠 Custom-trained RoBERTa model for sentiment classification
- 📚 Fine-tuned on Kaggle and Hugging Face sentiment datasets
- 🎞️ Emotion-aware movie recommendations
- 🎨 Clean and responsive web interface
- 📡 TMDB API integration for movie metadata and visuals

## 🤖 Sentiment Model Details

- Base Model: [`roberta-base`](https://huggingface.co/roberta-base)
- Fine-tuned using:
  - [Kaggle Sentiment140 Dataset](https://www.kaggle.com/datasets/kazanova/sentiment140)
  - [Hugging Face IMDb Reviews Dataset](https://huggingface.co/datasets/imdb)
- Framework: Hugging Face Transformers, PyTorch
- 27 different emotion classification for precise suggestions.

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Flask)
- **Model Serving:** Transformers + Torch
- **API:** TMDB for movie data
- **Version Control:** Git & GitHub

## 🚀 How It Works

1. User enters a sentence like _“I feel anxious and tired.”_
2. The RoBERTa model analyzes the sentiment.
3. Based on the emotion (positive, neutral, or negative), the system recommends a suitable list of movies.
4. The interface displays movie posters, descriptions, and links.


## 🧪 Example Inputs

| Input                             | Sentiment | Recommended Genre         |
|----------------------------------|-----------|---------------------------|
| "I'm feeling really low today."  | Bad  | Comedy, Inspirational     |
| "I'm so excited and hopeful!"    | Happy  | Adventure, Romance        |
| "Nothing much going on."         | Neutral   | Slice of life, Drama      |

## 🎓 Team

This project was developed as part of our undergraduate graduation thesis.

- **Serkan Acar** 
- **Irmak Koç** 


## 📷 Screenshot

![image](https://github.com/user-attachments/assets/a700f543-a8d9-41ee-b3dd-dc2f21a88af3)

## Training Results

![image](https://github.com/user-attachments/assets/3030ff78-6609-41eb-8eac-fb3c5f1f4d64)
![image](https://github.com/user-attachments/assets/aca108c5-6fca-432b-8f52-2c8500dbebb5)




## 📬 Contact

For questions or collaboration:

- GitHub: [https://github.com/serkanacr](https://github.com/serkanacr) [https://github.com/irmakkoc](https://github.com/irmakkoc)
- Email: [serkan.acar@stu.khas.edu.tr] [irmakkoc@stu.khas.edu.tr] 

---


