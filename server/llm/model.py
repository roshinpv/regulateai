from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import logging
import os

from .config import settings

logger = logging.getLogger(__name__)

# Create models directory if it doesn't exist
os.makedirs("models", exist_ok=True)

class LLMManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.model_path = settings.MODEL_PATH
        self.llm = None
        self.initialized = False
        
        # Try to initialize the model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the LLM model if the model file exists."""
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Model file not found at {self.model_path}. LLM will not be available.")
                return False
            
            # Set up callback manager for the LLM
            callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
            
            # Initialize the LLM
            self.llm = LlamaCpp(
                model_path=self.model_path,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                top_p=settings.TOP_P,
                top_k=settings.TOP_K,
                callback_manager=callback_manager,
                verbose=False,
                n_ctx=4096,  # Context window size
                n_gpu_layers=-1,  # Auto-detect GPU layers
                n_batch=512,  # Batch size for prompt processing
                f16_kv=True,  # Use half-precision for key/value cache
            )
            
            self.initialized = True
            logger.info(f"LLM initialized successfully with model: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            return False
    
    def is_initialized(self):
        """Check if the LLM is initialized and ready to use."""
        return self.initialized
    
    def get_llm(self):
        """Get the LLM instance."""
        if not self.initialized:
            if not self._initialize_model():
                raise ValueError("LLM is not initialized and could not be initialized.")
        return self.llm
    
    def generate_response(self, prompt, context=None):
        """Generate a response from the LLM based on the prompt and optional context."""
        if not self.initialized:
            if not self._initialize_model():
                return "I'm sorry, but the language model is not available at the moment. Please try again later."
        
        try:
            # Create the full prompt with context if provided
            if context:
                full_prompt = f"""You are an AI assistant specialized in regulatory compliance for financial institutions.
                
Context information:
{context}

User query: {prompt}

Based on the context information provided, please answer the user's query. If the context doesn't contain relevant information, say so and provide general information about the topic if possible."""
            else:
                full_prompt = f"""You are an AI assistant specialized in regulatory compliance for financial institutions.

User query: {prompt}

Please answer the user's query based on your knowledge of financial regulations and compliance requirements."""
            
            # Generate response
            response = self.llm.invoke(full_prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I'm sorry, but I encountered an error while processing your request. Please try again later."
    
    def create_chain(self, prompt_template):
        """Create an LLMChain with the given prompt template."""
        if not self.initialized:
            if not self._initialize_model():
                raise ValueError("LLM is not initialized and could not be initialized.")
        
        prompt = PromptTemplate.from_template(prompt_template)
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain

# Singleton instance
llm_manager = LLMManager()