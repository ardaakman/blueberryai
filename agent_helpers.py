import os
import openai
from utils import *

from dotenv import load_dotenv

from chat_agents import *

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class CallHandler():
    def __init__(self, call_id):
        self.call_id = call_id
        
        self.recipient, self.task_context = self.retrieve_task_and_recipient(self.call_id)
        
        self.context_manager = ContextManager()
        self.context_manager.sync_to_database(call_id)
        
        self.chat_agent = EfficientContextAgent(self.task_context, self.recipient, self.context_manager)
    
    @staticmethod
    def retrieve_task_and_recipient_from_db(call_id):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT context, recipient FROM call_log WHERE id = ?", (call_id,))
            task, recipient = cur.fetchone()
        
        return task, recipient
    
    @staticmethod
    def retrieve_dialogue_from_db(call_id):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, sender, message FROM chat WHERE call_id = ? ORDER BY id ASC", (call_id,))
            rows = cur.fetchall()

        dialogue = [(row['sender'], row['message']) for row in rows]
        return dialogue
        
    def load_dialogue(self):
        def format_dialogue_to_gpt(dialogue, customer_tag="callee", agent_tag="caller"):
            result = []
            for sender, message in dialogue:
                if sender == customer_tag:
                    entry = {"role": "user", "content": f"Customer Service Agent: {message}"}
                elif sender == agent_tag:
                    entry = {"role": "assistant", "content": f"{message}"}
                else:
                    raise Exception("Invalid sender tag.")
                
                result.append(entry)
            return result
            
        dialogue = self.retrieve_dialogue_from_db(self.call_id)
        gpt_dialogue_history = format_dialogue_to_gpt(dialogue)
        
        return gpt_dialogue_history

    def generate_response(self, customer_service_respond):
        # Update the context with the most recent one
        self.context_manager.sync_to_database(self.call_id)
        # Load the dialogue history
        self.chat_agent.dialogue_history = self.load_dialogue()
        # Use the chat-agent to get a response
        agent_response = self.chat_agent(customer_service_respond)
        # Return response
        return agent_response
    
    def call(self, customer_service_respond):
        return self.generate_response(customer_service_respond)
        

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
    
    def sync_to_database(self, call_id):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT personal_info FROM call_log WHERE id = ?", (call_id,))
            question_answers = cur.fetchone()[0]
    
        question_answers = question_answers.split('\n')
        self.context = question_answers
    
    def load_from_list(self, list_of_qa):
        self.context.extend([f"{q}: {a}" for q,a in list_of_qa])
    
    @staticmethod
    def generate_questions_from_task(task, model="gpt-3.5-turbo", num_questions=5):
        prompt = f"""
Given the context of {task}, what are some possible personal questions, 
such as date of birth, account number, etc. that the customer service agent might ask the user?
Phrase questions as key words, such as "Date of Birth". 

Limit your answers to {num_questions} questions. Do not number the questions. Just give questions seperated by a new line.
"""
        
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
    
    def get_dialogue_history_from_agent(self, agent):
        dialogue_history = agent.dialogue_history
        
        dialogue = ""
        for dialogue_dict in dialogue_history:
            if dialogue_dict["role"] == "user":
                dialogue += "\n" + dialogue_dict["content"]
            elif dialogue_dict["role"] == "assistant":
                dialogue += "\n" + "Human" + dialogue_dict["content"]
        return dialogue

    def get_dialogue_history_from_database(self, call_id): 
        def format_dialogue(dialogue, customer_tag="callee", agent_tag="caller"):
            result = []
            for sender, message in dialogue:
                if sender == customer_tag:
                    entry = {"role": "user", "content": f"Customer Service Agent: {message}"}
                elif sender == agent_tag:
                    entry = {"role": "assistant", "content": f"{message}"}
                else:
                    raise Exception("Invalid sender tag.")
                
                result.append(entry)
            return result
        
        dialogue = CallHandler.retrieve_dialogue_from_db(call_id)
        
    
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