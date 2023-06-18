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
    
    def generate_questions_from_task(self, task, recipient, model="gpt-3.5-turbo"):
        prompt = f"I want to {task} with {recipient}. What questions would they most likely ask me? Can you format your response such that there's one question on each line and no commentary?"
        
        messages = [{"role": "user", "content": prompt}]
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        questions = completion.choices[0].message.content.split("\n")
        questions = [q.strip() for q in questions]
        
        for q in questions:
            self.context.append((q, input(f"Enter the answer to the question - {q}: ")))
                                
        return questions
    
# TODO: Chat engine should keep track of both the context and the dialogue
# TODO: The dialogue is important for the classification task

# class OpenAIChatEngine(ABC):
#     def __init__(self, model, request_limit=1):
#         self.model = model
#         self.requests_till_error = request_limit
        
#     def set_agent_description(self, agent_description=""):
#         if len(agent_description) > 0:
#             return [{"role": "system", "content": agent_description}]
        
#     def __call__(self, messages, counter=0):        
#         try:
#             completion = openai.ChatCompletion.create(
#                 model=self.model,
#                 messages=messages
#             )
#             return completion.choices[0].message
#         except:
#             if counter < self.requests_till_error:
#                 return self.__call__(messages, counter+1)
#             else:
#                 return "I'm sorry, I'm having trouble understanding you. Could you rephrase your request?"

class Agent():
    def __init__(self, task, recipient, efficient_messages=True):
        self.task = task
        self.recipient = recipient
        
        # Setting to understand how to set up the messages
        self.efficient_messages = efficient_messages
        
        # Setup context manager's default value
        self.context_manager = None
        
        # Setup chat engine
        self.model = "gpt-3.5-turbo" 
        agent_description_prompt = f"You're imitating a human that is trying to {task} with {recipient}. Imagine you're on a call with their customer service. Sound like a human and use your context to return the appropriate response. You could use filler words like 'um' and 'uh' to sound more human."
        self.agent_description = [{"role": "system", "content": agent_description_prompt}]
        
        # Setup loggers to keep track of conversation and history
        self.messages = [self.agent_description]
        self.dialogue_history = []
        
    def connect_context(self, context_manager : ContextManager):
        self.context_manager = context_manager
        
    def prompt_enhance_with_context(self):
        if self.context_manager:
            context = "Here's information about the human you're imitating, you can use this to help you respond:"
            for c in self.context_manager.context:
                context += f"\n{c}"
            return context
        else:
            return ""
        
    def engineer_prompt(self, customer_service_response):
        context = self.prompt_enhance_with_context()
        
        ending_prompt = "If the call is over and you've resolved your issue, you can return 'bye' to end the call. If you are unsure about a question and need more information, you can return '/user help' to get assistance."
        formatting_prompt = "Pretend that you're speeking on the phone, so if you need to say any numbers, write them as digits with spaces in between. Like 5032 should be 5 0 3 2."
        
        customer_service_prompt = f"Customer Service Agent: {customer_service_response}"
        agent_response_prompt = f"Your Response:"
        
        components = [context, ending_prompt, formatting_prompt, customer_service_prompt, agent_response_prompt]
        return "\n".join(components)
    
    def generate_response(self, customer_service_response):
        new_dialogue_chain = {"role": "user", "content": customer_service_response}
        new_messages_chain = {"role": "user", "content": self.engineer_prompt(customer_service_response)}
        
        self.dialogue_history.append(new_dialogue_chain)
        self.messages.append(new_messages_chain)
        
        if self.efficient_messages:
            messages = [self.agent_description] + self.dialogue_history[:-1] + [new_messages_chain]
        else:
            messages = self.messages
        
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )
        print(completion.choices[0])
        response = completion.choices[0].message
        
        
        
        
    def __call__():
        pass
    
    def start_conversation(self):
        return self.generate_response("<silence from the customer service agent>")
    

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