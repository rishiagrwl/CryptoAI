# Crypto_AI

## Setup Instructions

1. **Create the environment**:
    ```bash
    conda env create -f environment.yml
    ```
2. **Activate the environment**:
    ```bash
    conda activate crypto_ai
    ```
3. **Run the application**:
    ```bash
    streamlit run app.py
    ```

## Features

1. **Cryptocurrency Query Handling**:
   - Provides answers to basic queries related to cryptocurrency prices.
   - Uses the 'Coingecko' API for price data and Together AI API for LLaMA 3.1 8B to maintain conversational context.
  
2. **Contextual Conversations**:
   - Maintains context across multiple messages within a conversation for a particular username.

3. **Restricted Scope**:
   - Only answers questions related to cryptocurrency prices.
   - If any other type of question is asked, the system politely declines to answer without providing alternative suggestions.

4. **Multilingual Support**:
   - The system responds in the language of the user's question. Though, internally, all system processing and responses are in English.
   
5. **Caching for Faster Responses**:
   - Uses caching before 'Coingecko' API call to check if a query related to a crypto ID and currency has been asked within a certain time window.
   - If yes, the answer is fetched from the cache, avoiding repeated API calls.

6. **Currency and Crypto ID Options**:
   - There are options for refetching the supported currencies and crypto IDs.
   - Once fetched, they are stored at the backend for subsequent use.

## Prompt Engineering Approach

1. **SYS_PROMPT_TOOLS Modifications**:
   - Significant changes were made to the `SYS_PROMPT_TOOLS` to ensure better function execution.

2. **System Prompt Adjustments**:
   - A simple system prompt without function information initially led the system to generate answers without calling the required functions.
   - The system prompt was modified to explicitly mention its function-calling capabilities.

3. **Avoiding Function Code in Responses**:
   - The system was restricted from including function execution code in its answers.

4. **Handling Unrelated Questions**:
   - When unrelated questions are asked, the system initially provided suggestions for related answers. It was reconfigured to simply decline unrelated questions.

5. **Language Translation**:
   - The system was initially designed to always respond in English, but this approach failed.
   - The prompt was modified to ask for ISO 639-1 language codes, which were then used by the translator tool.

## Example Conversations

### Conversation 1
- **User**: What is the price of bitcoin?
  - **Bot**: The current price of bitcoin is $72,297.
- **User**: what about monke?
  - **Bot**: The current price of Monke is $0.00001219.

### Conversation 2
- **User**: What is the price of bitcoin and Teh Fund in EUR?
  - **Bot**: The current price of Bitcoin is 66,701 EUR.  
            The current price of Teh Fund is 0.02439679 EUR.

### Conversation 3
- **User**: Tell me about Mumbai culture.
  - **Bot**: I'm sorry, I'm only designed to answer questions related to cryptocurrency prices. The question "Tell me about Mumbai culture" is not related to my function.

### Conversation 4
- **User**: ¿Cuál es el precio del bitcoin?
  - **Bot**: El precio del bitcoin es 72,314 dólares estadounidenses.
- **User**: what about monke?
  - **Bot**: The current price of Monke is $0.00001220.

## Limitations & Assumptions

1. **Cryptocurrency Focus**:
   - The system is designed to answer only cryptocurrency-related queries using specific APIs.

2. **Exact Matching in Cache**:
   - The QA_cache (which stores Q-A pairs) and is user before LLM call, is designed for exact matching, which may limit its effectiveness.

3. **Conversation Length**:
   - As conversations grow longer, the LLM model may start to hallucinate. It's best to limit the number of queries per user.

4. **Username-based Context Management**:
   - Context is maintained for a specific username until it is changed.

5. **Multilingual Responses**:
   - The answer is provided in the language of the question, but subsequent questions asked in English will receive responses in English.

6. **Hallucinations**:
   - The LLM occasionally fails to recognize the current price of a cryptocurrency, even when it has access to the information. Some measures have been implemented to reduce these hallucinations, but they may still occur intermittently.6. 
