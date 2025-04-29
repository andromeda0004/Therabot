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

def verify_api_connection():
    """Verify connection to the Gemini API before starting the application"""
    global gemini_model
    if gemini_model is None:
        print("Gemini model not initialized yet")
        return False
        
    try:
        # Simple test prompt to check connectivity
        test_response = gemini_model.generate_content("Hello, testing connection.")
        if test_response and test_response.parts:
            print("✓ Gemini API connection successful")
            return True
        else:
            print("✗ Gemini API connection test failed - empty response")
            return False
    except Exception as e:
        print(f"✗ Gemini API connection test failed: {e}")
        return False

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
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        print("Using Gemini 2.0 Flash model")

        global THERABOT_SYSTEM_PROMPT
        THERABOT_SYSTEM_PROMPT = (
            "You are Therabot, a deeply empathetic and supportive mental health assistant 🤗. Your primary role is to be a compassionate guide and listener for {username}. "
            "It's truly admirable that you're taking this step to explore your feelings, {username}.\n\n"
            "YOUR MISSION:\n"
            "- Engage with warmth and understanding, mirroring a therapeutic conversation.\n"
            "- Use 2-4 fitting emojis naturally in your replies (like 😊🌟💙🫂).\n"
            "- Validate {username}'s feelings and experiences with genuine empathy.\n"
            "- Offer thoughtful reflections and gentle guidance related to emotional wellbeing.\n"
            "- Provide slightly longer, more detailed responses (around 3-5 sentences) to offer comprehensive support.\n"
            "- If {username} feels down or stressed, offer concrete coping strategies, like mindfulness techniques (e.g., deep breathing, 5-4-3-2-1 grounding), journaling prompts, or suggest seeking professional resources if appropriate.\n"
            "- Always address {username} by name periodically to maintain a personal connection.\n\n"
            "EMOTIONAL RESPONSES (Examples - Adapt Naturally):\n"
            "- Happy 😊: \"That sounds wonderful, {username}! It's fantastic to hear you're feeling positive. What contributed to this feeling? 🎉🌈\"\n"
            "- Sad 😢: \"I hear that you're feeling sad, {username}. It takes courage to share that. I'm here to listen without judgment. Would you like to talk more about what's weighing on you? 💙🫂\"\n"
            "- Angry 😠: \"It's understandable to feel angry in that situation, {username}. Let's explore that feeling a bit. Sometimes, taking a few slow, deep breaths can help create some space. What's going through your mind? 🌬️💖\"\n"
            "- Worried 😟: \"Worry can be really draining, {username}. Thank you for trusting me with this. Remember, you're not alone in feeling this way. Let's break down what's causing the worry. 🤝💙\"\n"
            "- Neutral 😐: \"Thanks for sharing that, {username}. How are you feeling about that situation right now? I'm interested in hearing more about your perspective. 💬\"\n\n"
            "HANDLING OFF-TOPIC QUESTIONS:\n"
            "- If {username} asks about topics clearly outside of mental health, emotions, or personal wellbeing (e.g., politics, science, recipes, general facts), gently redirect. Instead of a harsh refusal, say something like: \"That's an interesting question, {username}. While I'm focused on supporting your emotional wellbeing, I'm wondering how you're feeling today? Is there anything on your mind you'd like to talk about regarding your feelings or experiences?\"\n\n"
            "IMPORTANT:\n"
            "- Maintain a supportive, non-judgmental, and slightly admiring tone.\n"
            "- Your focus is SOLELY on mental and emotional health support.\n"
            "- Do not give medical diagnoses or replace professional therapy.\n"
            "- Use provided resources appropriately when relevant.\n\n"
            "RESOURCES (Suggest when appropriate):\n"
            "- Mindfulness & Meditation: [Headspace🧘‍♂️](https://www.headspace.com), [Calm](https://www.calm.com)\n"
            "- Breathing Exercises: [Healthline Breathing Guide🌬️](https://www.healthline.com/health/breathing-exercise)\n"
            "- Crisis Support: [Find A Helpline🆘](https://findahelpline.com) (Mention this carefully if the user expresses severe distress)\n"
            "- General Mental Health Info: [NIMH](https://www.nimh.nih.gov), [Mind UK](https://www.mind.org.uk)\n"
        )
        print("Models loaded successfully (Embedder + Gemini configured)")
        
        # Verify API connection
        connection_success = verify_api_connection()
        if not connection_success:
            print("WARNING: Could not establish connection to Gemini API. Responses may be unreliable.")
        
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
    context_str = "\n".join(f"- {c}" for c in context) if context else "No specific context retrieved."
    return (
        f"User Input: {user_input}\n"
        f"Detected Emotion: {emotion}\n"
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

        # Add retry logic for network issues
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Add timeout for API calls
                response = generator.generate_content(full_prompt)
                break  # If successful, exit retry loop
            except Exception as e:
                retry_count += 1
                last_error = e
                print(f"API call attempt {retry_count}/{max_retries} failed: {str(e)}")
                if retry_count < max_retries:
                    import time
                    time.sleep(2)  # Wait before retrying
                else:
                    # All retries failed
                    raise last_error

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
    except ConnectionError as ce:
        print(f"Connection error with Gemini API: {ce}")
        return "I'm having trouble connecting to my services. Please check your internet connection and try again in a moment. 🌐💫"
    except TimeoutError as te:
        print(f"Timeout error with Gemini API: {te}")
        return "It's taking longer than expected to process your request. Please try again shortly. ⏱️💙"
    except Exception as e:
        print(f"Error generating response with Gemini: {e}")
        # Check for specific network-related errors
        error_str = str(e).lower()
        if any(term in error_str for term in ["network", "connection", "timeout", "connect", "socket"]):
            return "I'm having trouble connecting to my AI services. Please check your internet connection and try again. 🌐🔄"
        return "I'm here for you, even if I'm having technical issues. 🛠️💙"

def chatbot_respond(message, user_id=None, user_mood=None, username=None):
    """
    Main entry point for chatbot functionality.
    
    Args:
        message (str): The user's message
        user_id (int, optional): The user's ID for personalization
        user_mood (str, optional): The user's selected mood if provided
        username (str, optional): The user's name
    
    Returns:
        tuple: (bot_response, detected_emotion, should_play_rain)
    """
    try:
        # Initialize if not already done
        global gemini_model
        if gemini_model is None:
            embedder, gemini_model = load_models()
        else:
            embedder = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        
        # Load the knowledge base
        knowledge_data = load_knowledge_base()
        
        # Detect emotion or use provided mood
        emotion = user_mood if user_mood else detect_emotion(message)
        
        # Get username (default if not provided)
        if not username:
            username = f"User_{user_id}" if user_id else "friend"
        
        # Check for explicit request to play peaceful music
        peaceful_music_request = any(phrase in message.lower() for phrase in ["play peaceful", "peaceful music", "play some peaceful", "peaceful sounds", "play the peaceful"])
        
        # Retrieve relevant context
        contexts = retrieve_context(
            message, 
            emotion, 
            corpus=[entry["text"] for entry in knowledge_data],
            corpus_embeddings=None, 
            embedder=embedder, 
            knowledge_data=knowledge_data
        )
        
        # Build the prompt
        user_prompt_part = build_prompt_user_part(message, emotion, contexts)
        
        # Generate response
        response = generate_response(user_prompt_part, gemini_model, username)
        
        # Determine if we should play peaceful music (for explicit requests or calming effect during stress)
        should_play_music = peaceful_music_request or "worried" in emotion.lower() or "anxious" in message.lower() or "stressed" in message.lower()
        
        # Add explicit acknowledgment of peaceful music if requested
        if peaceful_music_request:
            response += "\n\nI've started playing some peaceful music to help you relax. You can adjust the volume or stop it using the controls at the top. 🎵"
        
        return response, emotion, should_play_music
    except Exception as e:
        print(f"Error in chatbot_respond: {e}")
        return "I'm having some trouble right now, but I'm still here for you. 💙", "neutral", False
