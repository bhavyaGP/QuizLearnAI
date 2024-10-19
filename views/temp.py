import json
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

GOOGLE_API_KEY = "AIzaSyCJ3mrkXKWMNbnQbmjch58tBpYru75xu6Q"
genai.configure(api_key=GOOGLE_API_KEY)

quiz_no = int(input("Enter the number of questions you want in the quiz: "))

# Define a generalized prompt template
prompt_template = f"""You are a YouTube video summarizer. You will be taking a transcript text,
summarizing the entire video in points (around 350 words), generating {quiz_no} questions with options. Make sure that questions start with Q1, Q2 and so on and all the options should end with a '.' even if the options are numeric in nature. Quiz should start with labeled Quiz Questions and the answer key should be generated separately.
Keep the format same for all the output . The transcript text is: """

# Function to fetch the transcript
def get_transcript(youtube_url, preferred_languages):
    try:
        video_id = youtube_url.split('v=')[-1]
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=preferred_languages)
        transcript = ' '.join([item['text'] for item in transcript_data])
        return transcript
    except Exception as e:
        return None

# Function to generate summary and quiz using the generative model
def generate_summary_and_quiz(transcript, prompt):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    # Lower temperature for consistent results
    response = model.generate_content(prompt + transcript)
    return response.text

# Function to clean up any escaped quotes and unwanted characters
def clean_text(text):
    return text.replace('\"', '"').replace('', '').replace('\n', ' ').replace('#', ' ').replace('*','').strip()

# Function to parse the quiz and answer key
def parse_quiz_and_answers(summary_quiz_text):
    if summary_quiz_text:
        # Clean up the summary and quiz text
        cleaned_text = clean_text(summary_quiz_text)

        # Initialize quiz and answer dictionaries
        quiz_questions = {}
        answer_key = {}
        question_count = 1
        current_question = None
        options = []

        # Check if "Quiz Questions:" and "Answer Key:" exist
        if cleaned_text:
            quiz_section = cleaned_text.split("Quiz Questions:")[1] if "Quiz Questions:" in cleaned_text else ""

            # Check if "Answer Key:" exists, if not, we handle accordingly
            if quiz_section:
                quiz_section, answer_section = quiz_section.split("Answer Key:")
                answer_section = answer_section.strip()
            else:
                answer_section = ""

            # Split the quiz section into individual questions (if formatted as Q1, Q2, etc.)
            lines = quiz_section.split('Q')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Handle questions and options
                if '?' in line:
                    if current_question:
                        # Pad options to ensure exactly 4 are present
                        while len(options) < 4:
                            options.append("")
                        quiz_questions[f"question{question_count}"] = {
                            "question": current_question,
                            "options": {
                                "a": options[0] if len(options) >= 0 else "",
                                "b": options[1] if len(options) >= 1 else "",
                                "c": options[2] if len(options) >= 2 else "",
                                "d": options[3] if len(options) >= 3 else ""
                            }
                        }
                        question_count += 1

                    # Start a new question
                    parts = line.split('?')
                    current_question = f"Q{parts[0].strip()}?"
                    option_text = parts[1] if len(parts) > 1 else ""

                    # Ensure that we properly split options after cleaning them
                    option_text_cleaned = clean_text(option_text)
                    print(option_text_cleaned)
                    options = [opt.strip() for opt in option_text_cleaned.split('.')]  # Split by '.' and clean
                else:
                    # Process additional lines as options
                    print("Hey")
                    options.extend([opt.strip() for opt in line.split('.') ])
            
            # Add the last question
            if current_question:
                while len(options) < 4:
                    options.append("")
                quiz_questions[f"question{question_count}"] = {
                    "question": current_question,
                    "options": {
                        "a": options[0],
                        "b": options[1],
                        "c": options[2],
                        "d": options[3]
                    }
                }

            # Process the answer key
            if answer_section:
                answer_count = 1
                for answer in answer_section.split('Q'):
                    answer = answer.strip()
                    if ':' in answer:
                        answer_key[f"answer{answer_count}"] = {"answer": answer.split(':', 1)[1].strip()}
                        answer_count += 1
            else:
                # If no "Quiz Questions:" section exists, return empty quiz and answer key
                return {}, {}

        return quiz_questions, answer_key
    else:
        return {}, {}


# Function to generate the full JSON result
def generate_json(youtube_link, quiz_no):
    transcript = get_transcript(youtube_link, ['hi']) or get_transcript(youtube_link, ['en'])

    if transcript:
        summary_and_quiz = generate_summary_and_quiz(transcript, prompt_template)

        # Clean the generated content
        summary_and_quiz_cleaned = clean_text(summary_and_quiz)

        # Split the result into summary, quiz, and answers
        summary_part = summary_and_quiz_cleaned.split("Quiz Questions:")[0].strip() #if "Quiz Questions:" in summary_and_quiz_cleaned else ""
        quiz_questions, answer_key = parse_quiz_and_answers(summary_and_quiz_cleaned)

        # Build the final JSON output
        result_json = json.dumps({
            'youtube_link': youtube_link,
            'summary': summary_part,
            'quiz': quiz_questions,
            'answer_key': answer_key
        }, indent=4)

        return result_json
    else:
        return json.dumps({'error': 'Failed to extract transcript in both Hindi and English.'}, indent=4)

# Main function to run the process
def main():
    youtube_link = input("Enter the YouTube video link: ")
    result_json = generate_json(youtube_link, quiz_no)
    print(result_json)

if __name__ == "_main_":
    main()