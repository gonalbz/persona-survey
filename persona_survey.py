import asyncio
import json
from typing import List, Dict
from datasets import load_dataset
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=1,
    api_key=os.getenv("OPENAI_API_KEY")
)

async def load_personas(num_personas: int = 100):
    """Load and return the specified number of personas."""
    dataset = load_dataset("proj-persona/PersonaHub", "instruction", split="train")
    # Randomly sample num_personas from the dataset
    selected_data = dataset.shuffle().select(range(min(num_personas, len(dataset))))
    
    # Convert the dataset items to the format we need
    personas = []
    for item in selected_data:
        # The dataset has 'input persona' as a string, we'll use it directly
        if isinstance(item, dict) and 'input persona' in item:
            personas.append(item['input persona'])
        else:
            # If the item is not in the expected format, create a basic persona
            personas.append(f"A person who is thoughtful and analytical.")
    
    return personas

async def enrich_persona_context(persona_text: str) -> str:
    """Enrich the persona context with additional behavioral patterns and traits."""
    system_prompt = """Given this persona description, analyze and extract:
    1. Key personality traits and values
    2. Likely background and experiences
    3. Professional expertise or interests
    4. Communication style and thought patterns
    5. Potential biases or unique perspectives
    
    Format the response as a natural extension of the original description, maintaining the same tone and style."""
    
    human_prompt = f"Persona description: {persona_text}"
    
    # Make the LLM call asynchronously
    enrichment = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])
    
    # Combine original persona with enrichment
    return enrichment.content

async def simulate_response(persona_text: str, question: str) -> Dict:
    """Generate a response from a persona."""
    # Enrich the persona context first
    enriched_persona = await enrich_persona_context(persona_text)
    
    prompt = f"""You are now embodying a real person with the following background:

{enriched_persona}



Question: {question}

Please respond in character, as if you are this person filling out a survey:"""

    # Make the LLM call asynchronously
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    return {
        "persona": enriched_persona,  
        "question": question,
        "response": response.content
    }

async def run_simulations(
    questions: List[str],
    num_personas: int = 100
) -> List[Dict]:
    """Run simulations for all personas across all questions."""
    all_results = []
    
    # Load the specified number of personas
    personas = await load_personas(num_personas)
    
    for question in questions:
        # Process all personas concurrently
        tasks = [simulate_response(persona, question) for persona in personas]
        results = await asyncio.gather(*tasks)
        all_results.extend(results)
    
    return all_results

async def save_results_async(results: List[Dict], filename: str = "survey_results.json"):
    """Save the survey results to a JSON file asynchronously."""
    def _write_file():
        try:
            filepath = filename
            print(f"Attempting to save results to: {os.path.abspath(filepath)}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Successfully saved {len(results)} results to {filepath}")
        except Exception as e:
            print(f"Error saving results: {str(e)}")
            print(f"Current working directory: {os.getcwd()}")
    
    # Run the file writing in a thread pool
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _write_file)

async def analyze_responses_async(results: List[Dict]):
    """Analyze responses asynchronously."""
    def _analyze():
        print("\n=== Survey Response Analysis ===")
        print(f"Total responses: {len(results)}")
        
        # Group responses by question
        questions = {}
        for result in results:
            if result["question"] not in questions:
                questions[result["question"]] = []
            questions[result["question"]].append(result["response"])
        
        # Print summary for each question
        for question, responses in questions.items():
            print(f"\nQuestion: {question}")
            print(f"Number of responses: {len(responses)}")
            print("Sample responses (first 2):")
            for response in responses[:2]:
                print(f"- {response[:150]}...")
            print()
    
    # Run the analysis in a thread pool
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _analyze)

async def main():
    """Main async function to coordinate all operations."""
    print("Running persona simulations...")
    
    # Example question for testing
    test_question = ["How would you describe your ideal weekend?"]
    
    # Run simulations
    responses = await run_simulations(questions=test_question, num_personas=2)
    
    # Save and analyze results concurrently
    await asyncio.gather(
        save_results_async(responses),
        analyze_responses_async(responses)
    )
    
    print("\nComplete results have been saved to 'survey_results.json'")

if __name__ == "__main__":
    asyncio.run(main())