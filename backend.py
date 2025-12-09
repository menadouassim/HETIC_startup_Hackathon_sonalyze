from groq import Groq
from dotenv import load_dotenv
import os

from config import MODEL

load_dotenv()


#JSON file reader
def read_file(file_path):
	with open(file_path, "r") as file:
		return file.read()

prompt=read_file("context.txt")

json_file=read_file("test_data_n1.json")

#Function to interact with the LLM

###### replace with json file transfer ######

def ask_LLM(chat_history):
	client = Groq(api_key=os.environ["GROQ_KEY"])

	stream_response = client.chat.completions.create(
	    messages=
		[
       
        {
            "role": "system",
            "content": prompt
            },
        # Set a user message for the assistant to respond to.
        {
            "role": "user",
            "content": chat_history,
        }
    ],
	    stream=True,
	    model=MODEL
	)

	return stream_response

def read_stream_response(stream_response):
	for chunk in stream_response:
		if chunk.choices[0].delta.content == None : continue
		print(chunk.choices[0].delta.content, end="")


if __name__ == "__main__":
	stream_response = ask_LLM(chat_history=json_file)
	read_stream_response(stream_response)