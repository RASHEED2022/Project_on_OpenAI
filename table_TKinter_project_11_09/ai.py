import openai
import json 
import spacy
import re
import time
import table_view
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv
import os

load_dotenv() 


# GET your API key
API_KEY = os.getenv("API_KEY")
WEB_NLP = os.getenv("WEB_NLP")

# Set your API key
openai.api_key = API_KEY #set as env key afterwards

# Load the spaCy English language model
nlp = spacy.load(WEB_NLP)

#set file names and respective variable 
response_file_path = "response.json"
format_file_path_1 = "format_1.txt"
format_file_path_2 = "format_2.txt"
json_file_path = "data.json"
final_json_file_path = "output.json"
tree_level = 1

def read_file(file_name):
    #Exception Handling for reading the file
    try:
        with open(file_name, 'r') as file:
            file_contents = file.read()
    except FileNotFoundError:
        print(f"The file '{file_name}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    #Return the file contents
    return file_contents

def write_data_into_file(data): 
    with open(response_file_path, "w") as file:
        file.write(data)

def query_AI_Assistant(prompt):   
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    try:
        
        print("Sending Query to OpenAI")
        # Send a request
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=conversation
            )
        except openai.error.RateLimitError:
            print("\nERROR 102: The usage limit for OpenAI has been exceeded!!! \nWait for 7 minutes\n")
            time.sleep(432)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=conversation
            )
        except Exception:
            time.sleep(20)
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=conversation
                )
        
            except Exception:
                time.sleep(30)
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=conversation
                )
        
    
    except Exception:
        print("\nERROR 101: The usage limit for OpenAI has been exceeded!!! \nWait for 7 minutes\n")
        time.sleep(432)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )
    
    # return the assistant's reply
    return (response['choices'][0]['message']['content'])

def get_keywords(data):
    topic=list(data.keys())[0]
    key_list = list(data[topic].keys())
    return data[topic][key_list[1]]  
    
def NLP_extract_topic(sentence):
    # Process the input sentence
    doc = nlp(sentence)

    # Initialize variables to store topic information
    topic = ""
    max_topic_freq = 0

    # Analyze named entities in the sentence
    entities = [ent.text for ent in doc.ents]

    # Extract noun phrases from the sentence
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]

    # Combine entities and noun phrases into a single list
    keywords = entities + noun_phrases

    # Create a frequency distribution of keywords
    keyword_freq = {}
    for keyword in keywords:
        if keyword in keyword_freq:
            keyword_freq[keyword] += 1
        else:
            keyword_freq[keyword] = 1

    # Find the most frequent keyword as the topic
    for keyword, freq in keyword_freq.items():
        if freq > max_topic_freq:
            topic = keyword
            max_topic_freq = freq

    return topic
   
def get_prompt(topic,description,data):
    
    file_contents = read_file(format_file_path_2)
    #converting the data into proper heading using NLP module
    topic = NLP_extract_topic(data)
    #Creating the prompt
    prompt = f"Expand the keyword: \"{topic}\" with respect to the main topic: {topic} and its description: {description} same as the below format: \n{file_contents}"
    
    return query_AI_Assistant(prompt)

def process_keywords(data, count, n):
    global tree_level
    if count == 0:
        tree_level -= 1
    
    topic=list(data.keys())[0]
    key_list = list(data[topic].keys())
    description = data[topic][key_list[0]]
    keywords = data[topic][key_list[1]]
    n= len(keywords) 
    keyword = keywords[count]
    
    new_data = get_prompt(topic,description,keyword) # {topic:{keywords:[data points}}
    if (tree_level>0):
        process_keywords(new_data,0,len(get_keywords(new_data)))
        tree_level += 1
    data[topic][key_list[1]][count] = new_data #topic:{keywords:[,,count=new_data,,,]}
    count += 1
    
    if n == count:
        return data
    
    process_keywords(data,count,n)

def run_ai_code(user_input): 
    print("Data Fetching....") 
    try: 
        #PARENT LEVEL OPERATION
        #Get the file_contents using the read_file function
        file_content = read_file(format_file_path_1)

        #Modeling the user input data
        prompt = f"write about {user_input} same as the below format: \n{file_content}"
        
        # Get the assistant's reply from the function query_AI_Assistant()
        assistant_reply = query_AI_Assistant(prompt)

        #editing the json file
        write_data_into_file(assistant_reply)


        #CHILD LEVEL OPERATIONS
        #Reading the json file 
        json_file_contents = read_file(response_file_path)

        # Start processing the keywords
        dict_key = json.loads(json_file_contents)
        
        process_keywords(dict_key, 0, len(get_keywords(dict_key)))

        with open(json_file_path, 'w') as json_file:
            json.dump(dict_key, json_file, indent=4)


        #Proper alignment of the json file in the new file named as output.json
        with open(json_file_path, 'r') as file:
            file_contents = file.read()

        prompt = f"make the below json file named as json_file into a proper json file and only return the proper json structure file: \njson_file: \n{file_contents}"
        reply  = query_AI_Assistant(prompt)

        # Use regular expressions to extract the JSON part within triple backticks
        json_match = re.search(r'```json(.*?)```', reply, re.DOTALL)
        
        if json_match:
            json_text = json_match.group(1)
            
            # Load the extracted JSON content
            try:
                with open(final_json_file_path,'w') as json_file:
                    json_file.write(json_text)
            except json.JSONDecodeError as e:
                print("Error parsing JSON:", str(e))
        else:
            with open(final_json_file_path, "w") as json_file:
                    json_file.write(reply)
            print("Data saved to",final_json_file_path)
        
    except Exception:
        print('Error occured in the code!!!')
    finally:
        #Creating table view of json file
        table_view.table()
    
# Check if this script is run directly
if __name__ == "__main__":
    run_ai_code()


