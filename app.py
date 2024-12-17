from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import json
import re
from langchain_groq import ChatGroq
import sys

formatter = TextFormatter()

def get_transcript(youtube_url):
    try:
        video_id = youtube_url.split('v=')[-1]
        transcript = None
        language = None

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
            language = 'hi'
        except:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                language = 'en'
            except:
                return {"error": "Neither Hindi nor English transcript is available."}, None

        return formatter.format_transcript(transcript), language
    except Exception as e:
        return {"error": f"Error fetching transcript: {str(e)}"}, None

# Updated function for cleaning JSON content
def clean_response_content(response_content):
    try:
        # Attempt to load the response content directly as JSON
        return json.loads(response_content)
    except json.JSONDecodeError:
        # If it's not valid JSON, attempt a basic cleanup
        cleaned_content = response_content.replace("'", '"')
        cleaned_content = re.sub(r',\s*([\]}])', r'\1', cleaned_content)
        return json.loads(cleaned_content)

def generate_summary_and_quiz(transcript, num_questions, language, difficulty):
    try:
        prompt = f"""
        Summarize the following transcript by identifying the key topics covered, and provide a detailed summary of each topic in 6-7 sentences.
        Each topic should be labeled clearly as "Topic X", where X is the topic name. Provide the full summary for each topic in English, even if the transcript is in a different language.

        After summarizing, create a quiz with {num_questions} multiple-choice questions in English, based on the transcript content.
        Only generate {difficulty} difficulty questions. Format the output in JSON format as follows, just give the JSON as output, nothing before it:

        {{
            "summary": {{
                "topic1": "value1",
                "topic2": "value2",
                "topic3": "value3"
            }},
            "questions": {{
                "{difficulty}": [
                    {{
                        "question": "What is the capital of France?",
                        "options": ["Paris", "London", "Berlin", "Madrid"],
                        "answer": "Paris"
                    }},
                    {{
                        "question": "What is the capital of Germany?",
                        "options": ["Paris", "London", "Berlin", "Madrid"],
                        "answer": "Berlin"
                    }}
                ]
            }}
        }}

        Transcript: {transcript}
        """

        llm = ChatGroq(
            model="llama3-groq-70b-8192-tool-use-preview",
            temperature=0,
            groq_api_key=""
        )
        response = llm.invoke(prompt)

        if hasattr(response, 'content'):
            response_content = response.content
            # Clean and parse the response content into valid JSON
            cleaned_content = clean_response_content(response_content)

            try:
                return cleaned_content  # Already a JSON dictionary
            except json.JSONDecodeError as e:
                return {"error": "Failed to parse JSON response."}
        else:
            return {"error": "Response does not have a 'content' attribute."}

    except Exception as e:
        return {"error": f"Error generating summary and quiz: {str(e)}"}

def main(youtube_link, num_questions, difficulty):
    transcript, language = get_transcript(youtube_link)

    if isinstance(transcript, dict) and "error" in transcript:
        return transcript  # Return error directly if there's an issue

    summary_and_quiz = generate_summary_and_quiz(transcript, num_questions, language, difficulty)

    if "error" in summary_and_quiz:
        return summary_and_quiz  # Return error if summary generation fails

    return summary_and_quiz  # Return the generated summary and quiz as a dictionary

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(1)

    youtube_link = sys.argv[1]
    num_questions = int(sys.argv[2])
    difficulty = sys.argv[3].lower()

    output = main(youtube_link, num_questions, difficulty)

    # Output the final result as JSON
    print(json.dumps(output, indent=4))  # Use `indent=4` for pretty printing



