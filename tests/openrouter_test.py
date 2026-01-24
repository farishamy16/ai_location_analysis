"""
OpenRouter integration test with LangChain
This file demonstrates how to use OpenRouter API with LangChain
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

def test_openrouter_basic():
    """Test basic OpenRouter connection with LangChain"""
    
    # Configure OpenRouter with LangChain
    # You need to set OPENROUTER_API_KEY in your environment variables
    model_name = "deepseek/deepseek-v3.2"  # You can change this to any OpenRouter model
    
    llm = ChatOpenAI(
        model = model_name,
        api_key=os.getenv("OPENROUTER_API_KEY") or "",  # type: ignore
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
    )

    print(f"🤖 Testing model: {model_name}")
    
    # Test basic message
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Hello! Can you tell me about OpenRouter?")
    ]
    
    try:
        response = llm.invoke(messages)
        print("✅ Basic test successful!")
        print(f"Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def test_openrouter_chain():
    """Test OpenRouter with LangChain chain"""
    
    llm = ChatOpenAI(
        model="anthropic/claude-3-haiku",
        api_key=os.getenv("OPENROUTER_API_KEY") or "",  # type: ignore
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
    )
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that specializes in {topic}."),
        ("human", "{question}")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    try:
        response = chain.invoke({
            "topic": "artificial intelligence",
            "question": "What are the main types of machine learning?"
        })
        print("\n✅ Chain test successful!")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"\n❌ Chain test failed: {e}")
        return False

def test_different_models():
    """Test different models available on OpenRouter"""
    
    models_to_test = [
        "anthropic/claude-3-haiku",
        "anthropic/claude-3-sonnet",
        "openai/gpt-3.5-turbo",
        "google/gemini-pro"
    ]
    
    for model in models_to_test:
        print(f"\n🔄 Testing model: {model}")
        
        llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENROUTER_API_KEY") or "",  # type: ignore
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
        )
        
        try:
            response = llm.invoke("Say hello in one sentence!")
            print(f"✅ {model}: {response.content}")
        except Exception as e:
            print(f"❌ {model}: Failed - {e}")

if __name__ == "__main__":
    print("🚀 Testing OpenRouter integration with LangChain...")
    
    # Check if API key is set
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ OPENROUTER_API_KEY not found in environment variables!")
        print("Please set your OpenRouter API key:")
        print("1. Create a .env file in the same directory")
        print("2. Add: OPENROUTER_API_KEY=your_api_key_here")
        exit(1)
    
    # Run tests
    test_openrouter_basic()
    # test_openrouter_chain()
    # test_different_models()
    
    print("\n🎉 Testing completed!")