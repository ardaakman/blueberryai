import os
import openai
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# TODO: Give account number as digits instead of the full number
# TODO: Prompt engineering to be as direct as possible
# TODO: It should be a lot more direct

class ContextManager():
    def __init__(self):
        self.context = []
        
    def set_agent_config(self):
        self.agent_description = f"""
            You're imitating a human that is trying to {self.task}. 
            You're on a call with {self.recipient} customer service.  
            Sound like a human and use your context to return the appropriate response.
            You could use filler words like 'um' and 'uh' to sound more human.
        """
        self.messages = []
        self.messages.append({"role": "system", "content": self.agent_description})
        
    def load_from_file(self):
        pass
    def load_from_directory(self):
        pass
    def load_from_database(self):
        pass
    
    def generate_questions_from_task(self):
        pass
    
class OpenAIChatEngine(ABC):
    def __init__(self, model):
        self.model = model
        self.messages = []
        
    @abstractmethod
    def set_agent_config(self):
        self.messages = []
        self.agent_description = ""
        self.messages.append({"role": "system", "content": self.agent_description})
        
    def __call__(self, prompt):
        self.messages.append({"role": "user", "content": prompt})
        
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages
        )
        return completion.choices[0].message
    
class ContextEnhancer(OpenAIChatEngine):
    def set_agent_config(self):
        self.agent_description = f"""
            Put yourself in the shoes of a customer service agent for {self.recipient}.
            A new caller wants to {self.task}. What questions might you ask them? 
            What personal information would you need to know? 
            
            In your response, hva e 
        """
        self.messages = []
        self.messages.append({"role": "system", "content": self.agent_description})
        

class Interaction():
    def __init__(self, task, context_directory):
        self.task = task
        self.context_directory = context_directory
        self.context = self.load_context(self.context_directory)
        
        print(self.context)
        
        self.messages = []
        
        # OpenAI Settings
        self.model = "gpt-3.5-turbo"

    def __repr__(self):
        return f"{self.role}: {self.content}"
    
    @staticmethod
    def load_context(directory):
        """Loads the context from the specified directory.

        Args:
            directory (str): The path to the directory containing text files.

        Returns:
            list of str: A list of strings containing the content of all the text files in the directory.
        """
        context = []
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and file_path.endswith('.txt'):
                with open(file_path, 'r') as file_handler:
                    text = file_handler.read()
                    context.append(text)
        return context
    
    def set_agent_config(self):
        self.agent_description = f"""
            You're imitating a human that is trying to {self.task}. 
            You're on a call with {self.recipient} customer service.  
            Sound like a human and use your context to return the appropriate response.
            You could use filler words like 'um' and 'uh' to sound more human.
        """
        self.messages = []
        self.messages.append({"role": "system", "content": self.agent_description})
    
    def __call__(self, response=None):
        # Initialize the agent
        self.set_agent_config()
        
        def step(customer_service_response):
            if customer_service_response == "":
                self.messages.append({"role": "user", "content": "Respond imagining you're a human. Imagine you're on a call with a customer service agent. Describe your problem and what you need help with. Be succint."})
            else:
                self.messages.append({"role": "user", "content": self.engineer_prompt(customer_service_response)})
                
            response = self.chat()
            print("BlueberryAI: ", response.content)
            self.messages.append(response)
            return response.content
        
        # While the conversation is still continuing
        if response is None:
            while True:
                customer_service_response = input("Customer Service Agent: ")
                step(customer_service_response)
        else:
            return step(response)
            
    def engineer_prompt(self, customer_service_response):
        """Generates the prompt for the engineer to respond to.
        """
        prompt = f"""
            You're imitating a human that is trying to {self.task}. 
            You're on a call with {self.recipient} customer service.  
            Sound like a human and use your context to return the appropriate response.
            You could use filler words like 'um' and 'uh' to sound more human.
    
            Customer Service Agent: 
            {customer_service_response}
            
            Here's information about the human you're imitating, you can use this to help you respond: 
            {self.context}
            
            Your response should be to the point and succint. Don't provide any personal information when not asked. 
            Represent numbers as digits with spaces in between. Like 5032 should be 5 0 3 2.
            
            Your Response:
        """
        return prompt
    
    def chat(self):
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages
        )
        return completion.choices[0].message

interaction = Interaction(task="create a new account", context_directory="twilio/")
interaction.recipient = "People's Gas"
interaction()

# data = SimpleDirectoryReader(input_dir="data/ekrem/").load_data()

# print(data)
# index = VectorStoreIndex.from_documents(data)
# print(index)

# chat_engine = index.as_chat_engine(chat_mode='react', verbose=True)

# task_explanation = "Hey I want to create a new account with People's Gas company."

# while True:
#     agent_input = input("Enter customer service request: ")
#     prompt = f"You're talking to a customer service agent. Your task is to {task_explanation}. Use your context to return the appropriate response.\n\Customer Service Agent: {agent_input}\nYour Response:"
#     response = chat_engine.chat(prompt)