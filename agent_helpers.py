import os
import openai

from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class ContextManager():
    def __init__(self):
        self.context = []
        
    def load_from_file(self, file_path):
        with open(file_path, 'r') as file_handler:
            text = file_handler.read()
            self.context.append(text)
            
    def load_from_directory(self, directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and file_path.endswith('.txt'):
                self.load_from_file(file_path)
    
    def load_from_database(self):
        pass
    
    def load_from_list(self, list_of_qa):
        self.context.extend([f"{q}: {a}" for q,a in list_of_qa])
    
    @staticmethod
    def generate_questions_from_task(task, model="gpt-3.5-turbo"):
        prompt = f"""Given the context of {task}, what are some possible personal questions, 
                    such as date of birth, account number, etc. that the customer service agent might ask the user?
                    Phrase questions as key words, such as "Date of Birth". Give multiple questions seperated by a new line."""
        
        messages = [{"role": "user", "content": prompt}]
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        questions = completion.choices[0].message.content.split("\n")
        questions = [q.strip() for q in questions]
                                
        return questions
    
class SummaryAgent():
    def __init__(self):
        self.model = "gpt-3.5-turbo" 
        self.generate_agent_description()
        self.agent_description = {"role": "system", "content": self.agent_description_prompt}
    
    def generate_agent_description(self):
        self.agent_description_prompt = f"""
Use the provided conversations delimited by triple quotes to answer questions.
You're given a conversation between a customer and a customer service representative.
Your goal is to summarize the conversation to actionable items. 
        """
        
    def engineer_prompt(self, dialogue_history):
        dialogue = ""
        for dialogue_dict in dialogue_history:
            if dialogue_dict["role"] == "user":
                dialogue += "\n" + dialogue_dict["content"]
            elif dialogue_dict["role"] == "assistant":
                dialogue += "\n" + "Human" + dialogue_dict["content"]
        
        prompt = f"""
You are a personal assistant. You're listening to a conversation between a human and a customer service representative. This dialogue is given between the triple quotes. Summarize the following dialogue to a list of important information provided by the customer service representative. This information shouldn't include anything the human would know before the conversation. Your response should be brief.
\"\"\"
{dialogue}
\"\"\"
"""
        return prompt
    
    def __call__(self, agent):
        dialogue_history = agent.dialogue_history
        
        prompt = self.engineer_prompt(dialogue_history)
        messages = [self.agent_description, {"role": "user", "content": prompt}]
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )
        response = completion.choices[0].message
        
        return response.content