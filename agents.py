from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url 
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def clean_content(content):
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
        return "\n".join(text_parts)
    return str(content)

def check_keys():
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    has_openai = openai_key is not None and openai_key.strip() != "" and openai_key != "your_openai_api_key_here"
    has_google = google_key is not None and google_key.strip() != "" and google_key != "your_google_api_key_here"
    return has_openai, has_google

def get_llm(provider: str = None):
    has_openai, has_google = check_keys()
    
    if provider is None:
        if has_google and not has_openai:
            provider = "Google Gemini"
        else:
            provider = "OpenAI"
            
    if "google" in provider.lower() or "gemini" in provider.lower():
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Default LLM based on auto-detection
llm = get_llm()

#1st agent 
def build_search_agent(provider: str = None):
    return create_agent(
        model = get_llm(provider),
        tools= [web_search],
        system_prompt="You are a research search agent. Find recent, reliable, and detailed information about the topic. Make sure to retrieve and output at least 2 source URLs."
    )

#2nd agent 
def build_reader_agent(provider: str = None):
    return create_agent(
        model = get_llm(provider),
        tools = [scrape_url],
        system_prompt="You are a reading and scraping agent. Extract content from relevant URLs to build deep research info."
    )


#writer chain 

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured, and insightful reports using markdown headers."),
    ("human", """Write a detailed research report on the topic below. 

CRITICAL REQUIREMENT: You MUST locate and list a minimum of 2 search source URLs/references in the report. If they are not present in the gathered research, please use your general knowledge of the domain to provide at least 2 relevant, high-quality URL references.

Topic: {topic}

Research Gathered:
{research}

Structure the report using markdown headers EXACTLY as follows:
## Introduction
[Provide background context and purpose of the report]

## Key Findings
[Provide at least 3 well-explained points]

## Conclusion
[Provide a summary of the findings]

## Sources
[List a minimum of 2 source URLs found in the research or relevant to the domain]

Be detailed, factual, and professional."""),
])

def get_writer_chain(provider: str = None):
    return writer_prompt | get_llm(provider) | StrOutputParser()

writer_chain = get_writer_chain()

#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

def get_critic_chain(provider: str = None):
    return critic_prompt | get_llm(provider) | StrOutputParser()

critic_chain = get_critic_chain()

