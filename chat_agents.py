import openai

class Agent():
    def __init__(self, task, recipient, context_manager):
        self.task = task
        self.recipient = recipient
        
        # Setup context manager's default value
        self.context_manager = context_manager
        
        # Setup chat engine
        
    def generate_agent_description(self, task, recipient):
        pass

    def generate(self):
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
            )
            value = completion.choices[0].message['content']
            return value
        except:
            return "Sorry, I don't understand. Can you repeat that?"

        
    def __call__(self, customer_service_response):
        pass

    
class ContextAgent(Agent):
    def __init__(self, task, recipient, context_manager):
        super().__init__(task, recipient, context_manager)
        
        self.model = "gpt-3.5-turbo" 
        self.generate_agent_description()
        self.agent_description = {"role": "system", "content": self.agent_description_prompt}
        
        # Setup loggers to keep track of conversation and history
        self.messages = [self.agent_description]
        self.dialogue_history = []
    
    def generate_agent_description(self):
        self.agent_description_prompt = f"""
            You're imitating a human that is trying to {self.task}. 
            You're on a call with {self.recipient} customer service.  
            Sound like a human and use your context to return the appropriate response.
            You could use filler words like 'um' and 'uh' to sound more human.
        """
    
    def __call__(self, customer_service_response):
        self.messages.append({"role": "user", "content": self.engineer_prompt(customer_service_response)})
        
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages
        )
        response = completion.choices[0].message
        self.messages.append(response)
        
        return response.content
    
            
    def engineer_prompt(self, customer_service_response):
        """Generates the prompt for the engineer to respond to.
        """
        context = '\n'.join(self.context_manager.context)
        prompt = f"""
You're imitating a human that is trying to {self.task}. 
You're on a call with {self.recipient} customer service.  
Sound like a human and use your context to return the appropriate response.
You could use filler words like 'um' and 'uh' to sound more human.

Here's information about the human you're imitating, you can use this to help you respond: 
{context}

Your response should be to the point and succint. Don't provide any personal information when not asked. 
Represent numbers as digits with spaces in between. Like 5032 should be 5 0 3 2.
If the agent asks for you to spell something out, you should respond with letters seperated by spaces. Like A P P L E.

Customer Service Agent: 
{customer_service_response}

Your Response:
        """
        return prompt
    
class EfficientContextAgent(Agent):
    def __init__(self, task, recipient, context_manager):
        super().__init__(task, recipient, context_manager)
        
        self.model = "gpt-3.5-turbo" 
        self.generate_agent_description()
        self.agent_description = {"role": "system", "content": self.agent_description_prompt}
        
        # Setup loggers to keep track of conversation and history
        self.messages = [self.agent_description]
        self.dialogue_history = []
    
    def generate_agent_description(self):
        self.agent_description_prompt = f"""
            You're imitating a human that is trying to {self.task}. 
            You're on a call with {self.recipient} customer service.  
            Sound like a human and use your context to return the appropriate response.
            You could use filler words like 'um' and 'uh' to sound more human.
        """
    
    def __call__(self, customer_service_response):
        self.dialogue_history.append({"role": "user", "content": f"Customer Service Agent: {customer_service_response}"})
        messages = [self.agent_description] + self.dialogue_history + [{"role": "user", "content": self.engineer_prompt(customer_service_response)}]
        
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )
        response = completion.choices[0].message
        self.dialogue_history.append(response)
        
        return response.content
    
    def engineer_prompt(self, customer_service_response):
        """Generates the prompt for the engineer to respond to.
        """
        context = '\n'.join(self.context_manager.context)
        prompt = f"""
You're imitating a human that is trying to {self.task}. 
You're on a call with {self.recipient} customer service.  
Sound like a human and use your context to return the appropriate response.
You could use filler words like 'um' and 'uh' to sound more human.

Here's information about the human you're imitating, you can use this to help you respond: 
{context}

Your response should be to the point and succint. Don't provide any personal information when not asked. 
Represent numbers as digits with spaces in between. Like 5032 should be 5 0 3 2.
If the agent asks for you to spell something out, you should respond with letters seperated by spaces. Like A P P L E.

Customer Service Agent: 
{customer_service_response}

Your Response:
        """
        return prompt
    
class EfficientAgent(Agent):
    def __init__(self, task, recipient, context_manager):
        super().__init__(task, recipient, context_manager)
        
        self.model = "gpt-3.5-turbo" 
        self.generate_agent_description()
        self.agent_description = {"role": "system", "content": self.agent_description_prompt}
        
        # Setup loggers to keep track of conversation and history
        self.messages = [self.agent_description]
        self.dialogue_history = []
    
    def generate_agent_description(self):
        self.agent_description_prompt = f"""
            You're imitating a human that is trying to {self.task} with {self.recipient}. 
            You're on a call with customer service.  
            Sound like a human and use your context to return the appropriate response. Keep responses short, simple, and informal.
            You could use filler words like 'um' and 'uh' to sound more human. To end the call, just return 'bye'. 
            
            Your response should be to the point and succint. Don't provide any personal information when not asked. 
            Represent numbers as digits with spaces in between. Like 5032 should be five zero three two.
        """
    
    def __call__(self, customer_service_response):
        self.dialogue_history.append({"role": "user", "content": f"Customer Service Agent: {customer_service_response}"})
        self.messages.append({"role": "user", "content": self.engineer_prompt(customer_service_response)})
        
        messages = self.messages[:1] + self.dialogue_history[:-1] + self.messages[-1:]
        
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )
        response = completion.choices[0].message
        self.messages.append(response)
        self.dialogue_history.append(response)
        
        return response.content
    
    def engineer_prompt(self, customer_service_response):
        """Generates the prompt for the engineer to respond to.
        """
        context = '\n'.join(self.context_manager.context)
        prompt = f"""
Here's information about the human you're imitating, you can use this to help you respond: 
{context}

Your response should be to the point and succint. Represent numbers as digits with spaces in between. Like 5032 should be 5 0 3 2. 
If the customer service agent asks for you to spell something out, say spell out "APPLE", you should respond with letters seperated by spaces. Like A P P L E.

You're imitating a human that is trying to {self.task}. Come up with the best response to the customer service agent below. 

Customer Service Agent: 
{customer_service_response}

Your Response:
        """
        return prompt