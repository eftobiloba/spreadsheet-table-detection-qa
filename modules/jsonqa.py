from langchain_community.document_loaders import JSONLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import GPT4All
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class JsonQuestionAnswering:
    def __init__(self, json_file_path, model_path, embedding_model="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initializes the JosnQuestionAnswering system with JSON data, embeddings, and LLM model.
        :param json_file_path: Path to the JSON file containing quiz data.
        :param model_path: Path to the GPT4All model.
        :param embedding_model: Hugging Face embedding model to use.
        """
        self.json_file_path = json_file_path
        self.model_path = model_path
        self.embedding_model = embedding_model
        self.vector_store = None
        self.qa_chain = None
        
        self.load_json()
        self.setup_vector_store()
        self.load_model()
        self.setup_qa_chain()
    
    def load_json(self):
        """Loads JSON data into LangChain."""
        loader = JSONLoader(file_path=self.json_file_path, jq_schema='.tables[]', text_content=False)
        self.documents = loader.load()
    
    def setup_vector_store(self):
        """Creates embeddings and vector store from the loaded documents."""
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        self.vector_store = FAISS.from_documents(self.documents, embeddings)
    
    def load_model(self):
        """Initializes the GPT4All model."""
        self.llm = GPT4All(model=self.model_path, n_threads=8, verbose=True)
    
    def setup_qa_chain(self):
        """Creates the retrieval-based QA chain."""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})  # 👈 limit retrieved context
        self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=retriever)
        
        # Define a custom prompt
        custom_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="Use the following extracted table data as context:\n\n{context}\n\nNow, answer this question: {question}"
        )
        self.qa_chain.combine_documents_chain.llm_chain.prompt = custom_prompt

    
    def ask_question(self, query):
        """Runs the QA system to answer a given query."""
        return self.qa_chain.run(query)

# Example Usage
if __name__ == "__main__":
    json_path = "tables.json"
    model_path = "models/ggml-nomic-ai-gpt4all-falcon-Q4_0.gguf"
    
    qa_system = JsonQuestionAnswering(json_file_path=json_path, model_path=model_path)
    
    print("\n🔍 Ask a question:")
    user_question = input("> ")
    answer = qa_system.ask_question(user_question)
    print("\n💡 Answer:", answer)