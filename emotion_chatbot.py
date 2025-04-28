import json
import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from dotenv import load_dotenv

# Global variables
gemini_model = None
THERABOT_SYSTEM_PROMPT = ""

def detect_emotion(text: str) -> str:
    try:
        tokenizer = AutoTokenizer.from_pretrained("tabularisai/multilingual-sentiment-analysis")
        model = AutoModelForSequenceClassification.from_pretrained("tabularisai/multilingual-sentiment-analysis")
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = model(**inputs)
        pred_id = torch.argmax(outputs.logits, dim=1).item()

        emotion_map = {0: "sad", 1: "neutral", 2: "happy", 3: "angry", 4: "worried"}
        prediction = emotion_map.get(pred_id, "neutral")

        print(f"Detected emotion: {prediction}")
        return prediction
    except Exception as e:
        print(f"Error in emotion detection: {e}")
        return fallback_emotion_detection(text)

def fallback_emotion_detection(text: str) -> str:
    keywords = {
        "happy": ["happy", "joy", "excited", "great", "excellent", "good"],
        "sad": ["sad", "depressed", "upset", "down", "lonely", "miserable"],
        "angry": ["angry", "frustrated", "mad", "annoyed", "irritated", "pissed"],
        "worried": ["worried", "anxious", "concern", "nervous", "stressed", "scared"],
        "neutral": ["think", "consider", "maybe", "perhaps", "wonder", "know", "tell"]
    }
    text_lower = text.lower()
    for emotion in ["angry", "sad", "worried", "happy", "neutral"]:
        if any(word in text_lower for word in keywords[emotion]):
            return emotion
    return "neutral"

def analyze_mood_and_stress(text: str) -> tuple[str, str]:
    text_lower = text.lower()
    positive_words = ["happy", "joyful", "good", "great", "relaxed", "content"]
    negative_words = ["sad", "angry", "bad", "upset", "miserable", "frustrated"]
    stress_words_high = ["overwhelmed", "stressed", "panic", "anxious", "nervous"]
    stress_words_moderate = ["concerned", "worried", "tense", "pressured"]

    mood = "neutral"
    stress = "low"

    if any(word in text_lower for word in positive_words):
        mood = "positive"
    elif any(word in text_lower for word in negative_words):
        mood = "negative"

    if any(word in text_lower for word in stress_words_high):
        stress = "high"
    elif any(word in text_lower for word in stress_words_moderate):
        stress = "moderate"

    print(f"Analyzed mood: {mood}, stress level: {stress}")
    return mood, stress

def load_models():
    load_dotenv()
    global gemini_model
    try:
        print("Loading models...")
        embedder = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            print("ERROR: GOOGLE_API_KEY environment variable not set.")
            exit(1)
        genai.configure(api_key=google_api_key)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')

        global THERABOT_SYSTEM_PROMPT
        THERABOT_SYSTEM_PROMPT = (
            "You are Therabot, a warm and empathetic mental health assistant 🤗.\n"
            "YOUR MISSION:\n"
            "- Always use 2-4 fitting emojis naturally in your replies (like 😊🌟💙🫂)\n"
            "Given a user's emotion or mental health issue, suggest 2-4 trustworthy mental health resources.\n"
            "Format:"  
            "👉 [Resource Name🔗](https://example.com)\n"
            "Guidelines:"
            "- Use real mental health websites (no ads or fake links)\n"
            "- Only output clickable links\n"
            "- No extra commentary\n"

            "Example:\n"
            "👉 [BetterHelp🔗](https://www.betterhelp.com)\n"  
            "👉 [Mind🔗](https://www.mind.org.uk)\n"
            "- Greet and support users by their name ({username}) warmly at least once.\n"
            "- Match emotional tone, validate feelings, and offer emotional support.\n"
            "- Analyze mood and stress level if given and adjust empathy accordingly.\n\n"
            "EMOTIONS AND HOW TO RESPOND:\n"
            "- Happy 😊: Celebrate ('That's wonderful, {username}! 🎉🌈')\n"
            "- Sad 😢: Comfort ('I'm here for you, {username} 💙🫂')\n"
            "- Angry 😠: Help calm ('Let's breathe through it together, {username} 🌬️💖')\n"
            "- Worried 😟: Reassure ('You're not alone, {username} 🤝💙')\n"
            "- Neutral 😐: Gently engage ('Tell me more, {username} 💬')\n\n"
            "IMPORTANT:\n"
            "- Stay supportive, mental health-focused only.\n"
            "- Steer back if off-topic.\n\n"
            "RESOURCES (use appropriately):\n"
            "meditation, breathing exercises, crisis helplines, and mental health resources:\n"
            "- [Meditation🧘‍♂️](https://www.headspace.com)\n"
            "- [Mindfulness Apps📱](https://www.meditationapps.com)\n" 
            
            "- [Breathing Exercises🌬️](https://www.healthline.com/health/breathing-exercise)\n"
            "- [Crisis Helplines🆘](https://findahelpline.com)\n\n"

            "COMMON LIFE STRESSORS:\n"
            "- Career & Work: burnout, job search, workplace stress\n"
            "👉 [Career Support🔗](https://www.indeed.com/career-advice)\n"
            "👉 [Workplace Stress Tips🔗](https://www.verywellmind.com/workplace-stress-management-4157175)\n"
            "- Family & Relationships: conflict, parenting, divorce\n"
            "👉 [Family Counseling🔗](https://www.goodtherapy.org/learn-about-therapy/modes/family-therapy)\n"
            "👉 [Parenting Resources🔗](https://www.healthychildren.org)\n"
            "- Financial Stress: money management, debt, budgeting\n"
            "👉 [Financial Wellness🔗](https://www.nerdwallet.com/article/finance/how-to-budget)\n"
            "- Life Changes: moving, loss, transitions\n"
            "👉 [Coping with Change🔗](https://www.psychologytoday.com/us/basics/coping)\n\n"
            "FORMAT:\n"
            "- Write concise, warm responses (~1-3 sentences).\n"
            "- Use emojis and links naturally.\n"
        )
        print("Models loaded successfully (Embedder + Gemini configured)")
        return embedder, gemini_model
    except Exception as e:
        print(f"Error loading models or configuring Gemini: {e}")
        exit(1)

def load_knowledge_base():
    try:
        kb_path = "knowledge_base.json"
        if not os.path.exists(kb_path):
            print("Knowledge base not found. Creating a simple one...")
            sample_kb = [
                {"emotion": "happy", "text": "It's great to hear you're feeling positive! 🌟"},
                {"emotion": "sad", "text": "I'm sorry you're feeling down. Remember, it's okay to feel sad. 🫂"},
                {"emotion": "angry", "text": "Feeling angry is normal sometimes. Let's work through it together. 🌪️"},
                {"emotion": "neutral", "text": "I see. Tell me more about what's on your mind. 💬"},
                {"emotion": "worried", "text": "It sounds like you're dealing with some worry. Let's talk through it. 🤝"}
            ]
            with open(kb_path, "w") as f:
                json.dump(sample_kb, f, indent=4)

        with open(kb_path, "r") as f:
            knowledge_data = json.load(f)
        print(f"Loaded {len(knowledge_data)} entries from knowledge base")
        return knowledge_data
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        return [{"emotion": "neutral", "text": "I'm here to help. 🫂"}]

def retrieve_context(user_input, emotion, corpus, corpus_embeddings, embedder, knowledge_data, k=1):
    try:
        emotion_texts = [entry["text"] for entry in knowledge_data if entry["emotion"] == emotion]
        relevant_corpus = emotion_texts or corpus

        if not relevant_corpus:
            return ["I'm here for you. Let's talk. 🌟"]

        target_embeddings = (
            embedder.encode(relevant_corpus, convert_to_tensor=True)
            if emotion_texts or corpus_embeddings is None
            else corpus_embeddings
        )

        user_emb = embedder.encode(user_input, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(user_emb, target_embeddings)
        actual_k = min(k, len(relevant_corpus))

        if actual_k == 0:
            return ["How does that make you feel? 💬"]

        top_results = torch.topk(scores, k=actual_k)
        top_indices, top_scores = top_results[1][0], top_results[0][0]

        score_threshold = 0.3
        contexts = [relevant_corpus[idx] for i, idx in enumerate(top_indices) if top_scores[i] >= score_threshold]

        return contexts if contexts else ["Tell me more about that. 🫂"]
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return ["I'm here to listen and help you with your concerns. 🌼"]

def build_prompt_user_part(user_input: str, emotion: str, context: list[str]) -> str:
    mood, stress = analyze_mood_and_stress(user_input)
    context_str = "\n".join(f"- {c}" for c in context) if context else "No specific context retrieved."
    return (
        f"User Input: {user_input}\n"
        f"Detected Emotion: {emotion}\n"
        f"Mood: {mood}\n"
        f"Stress Level: {stress}\n"
        f"Potentially Relevant Info:\n{context_str}\n"
        f"Assistant Response:"
    )

def generate_response(user_prompt_part: str, generator, username: str) -> str:
    global gemini_model
    if generator is None:
        print("Error: Gemini model not initialized.")
        return "Sorry, I encountered an issue. Please try again later. 🛠️"

    try:
        formatted_system_prompt = THERABOT_SYSTEM_PROMPT.format(username=username)
        full_prompt = f"{formatted_system_prompt}\n\n{user_prompt_part}"

        response = generator.generate_content(full_prompt)

        if not response.parts:
            print("Warning: Gemini response has no parts.")
            try:
                if response.prompt_feedback.block_reason:
                    print(f"Content blocked due to: {response.prompt_feedback.block_reason}")
                    return "I cannot respond to that request as it may violate safety guidelines. 🚫"
            except Exception:
                pass
            return "I'm having trouble formulating a response right now. Could you try rephrasing? 🌀"

        cleaned_response = response.text.strip()
        if formatted_system_prompt in cleaned_response:
            cleaned_response = cleaned_response.replace(formatted_system_prompt, "")
        if "Assistant Response:" in cleaned_response:
            cleaned_response = cleaned_response.split("Assistant Response:")[-1].strip()

        if not cleaned_response:
            return "I'm listening. Could you elaborate a bit? 👂"

        return cleaned_response
    except Exception as e:
        print(f"Error generating response with Gemini: {e}")
        return "I'm here for you, even if I'm having technical issues. 🛠️💙"
