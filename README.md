## Video Demo
https://youtu.be/95xvfj3fRaI

## Inspiration
Phone calls are annoying, yet a lot of companies still operate with customer service call centers. We wait minutes on end to get trivial tasks done, whether it's opening a new account with Xfinity or scheduling an appointment with your hospital. BlueberryAI is a personal AI secretary that makes calls for you, saving you time and effort. Blueberry could call any number and handle any task.

## What it does
BlueberryAI first asks you to explain the task, it then generates a list of questions that it thinks will be important to handle the task. This could include your account number or the last 4 digits of your SSN. After the user submits the answers, Blueberry places a call and talks with the customer service agent to handle your request. While on the call, the conversation is transcribed and presented to be monitored by the user with a beautiful UI.

## How we built it
BlueberryAI could be divided into three components: the front end, the phone call backend, and the conversational AI. The front end is built with HTML, this is the interface that the users assign a task to BlueberryAI. We have our own server that communicates with Twillo to handle phone calls. Flask connects the front end to the server. The conversational AI is a pipeline consisting of a listener, the chat engine, and the speaker. The listener takes an audio file and transcribes it; the listener utilizes chunking to parallelize transcription. The chat engine is built with a wrapper around the OpenAI GPT-3.5 model and keeps track of context. The speaker takes a response from the chat engine and creates a realistic audio file with Filiki API.

## Accomplishments that we’re proud of
The first thing we are very proud of is just the fact we build this while being completely new to some of the tools we used. Tools like hume (which we are able to use as an alternative to whisper in our codebase), or twilio were very new to us, but we could just adapt to these and build out a complete product. Another aspect that fills us with pride is how swiftly we identified a compelling idea that resonated with all team members. Despite initially exploring diverse industries and concepts, we quickly converged on an idea that captivated us collectively. This allowed us to focus our efforts and enhance the chosen concept collaboratively, benefiting from each team member's unique perspectives and skills. Lastly, we take great pride in the scale and complexity of our project, as well as the diverse range of tools we employed. As the project progressed, its size expanded rapidly, necessitating extensive code development. However, we were able to maintain agility by continuously testing and evaluating different options, ultimately identifying the most effective approaches and solutions.

## Challenges we ran into
We faced significant challenges while working with the Twilio API and developing our conversational agent's context management suite. The Twilio API proved to be inflexible and initially difficult to comprehend. Understanding its intricacies was a hurdle we had to overcome at the beginning of the project. Additionally, while we had achieved basic chat functionality early on, we encountered difficulties in storing and managing the context provided by OpenAI. It was essential for us to retain context between interactions without incurring significant delays. To address these challenges, we adopted a strategy of simplifying our Twilio implementation. By focusing on streamlined functionality and avoiding complex features that could introduce additional complexities into our codebase, we aimed to mitigate the difficulties associated with Twilio's API. Regarding the context management suite for our conversational agent, we iterated through various approaches to find the optimal solution. We recognized the importance of efficiently handling and preserving context throughout the conversation flow. Through experimentation and persistence, we were able to refine our approach to reach the most effective implementation.

## What we learned
One fundamental learning was when bumping into an area that might be a roadblock, making the other parts of the project work seamlessly so we can both gain momentum and produce a full product. We had moments where that one API we were working with was causing a lot of problems for us, and we handled this by focusing on other aspects of the project and coming back to that specific problem later on.

## What’s next for Blueberry AI
We think that given that we can make the tool even faster and more accurate, it can be a very useful app for everyone to just keep on their phones - sort of like a personal secretary. Furthermore, our tool can also be built to be used for companies as well to make customer support a less labor-intensive process - where one agent can monitor multiple chats.

## DevPost Link
https://devpost.com/software/blueberry-ai