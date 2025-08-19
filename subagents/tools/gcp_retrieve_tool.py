import os
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

import vertexai
from vertexai.preview import rag
from typing import Dict, Optional, Any

from google.oauth2.service_account import Credentials

load_dotenv()

def gcp_retrieve(
    query_text: str,
    corpus_disp_name_list: List[str],
    top_k_per_corpus: Optional[int] = None,
    vector_distance_threshold: Optional[float] = None
) -> Dict[str, Any]:
    """
    Retrieve top matching documents from one or more Google Cloud RAG-managed vector corpus indices using semantic similarity search.

    Args:
        query_text (str): The search query to embed and retrieve relevant documents for.
        corpus_disp_name_list (List[str]): List of corpus display names to search within. Only corpora with display names matching this list will be queried.
        top_k_per_corpus (Optional[int]): The maximum number of top similar documents to retrieve per corpus (default: 1).
        vector_distance_threshold (Optional[float]): Threshold for vector similarity. Lower values return more similar results (default: 0.5).

    Returns:
        Dict[str, Any]: A dictionary containing:
            - status (str): "success" or "error"
            - results (List[Dict]): Flattened list of top matched documents from all corpora
            - corpus_results (Dict): Detailed results mapped per corpus
            - searched_corpora (List[str]): Names of corpora that were searched
            - citations_summary (List[str]): Human-readable summary of corpus search coverage
            - count (int): Total number of documents retrieved
            - query (str): The original query
            - message (str): Summary message of the retrieval operation
            - citation_note (str): Note about citation format in results

    Example:
        >>> await gcp_retrieve(
        ...     query_text="What are the company's holiday policies?",
        ...     corpus_disp_name_list=["Employee Handbook", "HR Policy Corpus"],
        ...     top_k_per_corpus=3,
        ...     vector_distance_threshold=0.45
        ... )
        {
            "status": "success",
            "count": 6,
            "message": "Found 6 results for query 'What are the company's holiday policies?' across 2 corpora",
            "results": [
                {
                    "chunk": "...",
                    "corpus_name": "Employee Handbook",
                    "corpus_id": "abc123",
                    "relevance_score": 0.92,
                    "citation": "[Source: Employee Handbook (abc123)] File: holidays_policy.pdf"
                },
                ...
            ]
        }

    This tool uses Google Cloud's Vertex AI Embeddings and RAG Managed Database to provide relevant context and citations for RAG agents, enterprise chatbots, or document search assistants.
    """
    # gcp_credentials_path = os.getenv("gcp_credentials_path")
    if top_k_per_corpus is None:
        top_k_per_corpus = os.getenv("RAG_DEFAULT_SEARCH_TOP_K")
    if vector_distance_threshold is None:
        vector_distance_threshold = os.getenv("RAG_DEFAULT_VECTOR_DISTANCE_THRESHOLD")
    # Ensure types are correct for downstream API
    try:
        top_k_per_corpus = int(top_k_per_corpus)
    except Exception:
        top_k_per_corpus = 1
    try:
        vector_distance_threshold = float(vector_distance_threshold)
    except Exception:
        vector_distance_threshold = 0.5
    try:
        # First, list all available corpora
        corpora_response = list_rag_corpora()
        if corpora_response["status"] != "success":
            return {
                "status": "error",
                "error_message": f"Failed to list corpora: {corpora_response.get('error_message', '')}",
                "message": "Failed to search all corpora - could not retrieve corpus list"
            }
        
        all_corpora = corpora_response.get("corpora", [])
        
        if not all_corpora:
            return {
                "status": "warning",
                "message": "No corpora found to search in"
            }
        
        # Search in each corpus
        all_results = []
        corpus_results_map = {}  # Map of corpus name to its results
        searched_corpora = []

        for corpus in all_corpora:
            corpus_id = corpus["id"]
            corpus_name = corpus.get("display_name", corpus_id)

            if corpus_name in corpus_disp_name_list:
                # Query this corpus
                corpus_results = query_rag_corpus(
                    corpus_id=corpus_id,
                    query_text=query_text,
                    top_k=top_k_per_corpus,
                    vector_distance_threshold=vector_distance_threshold
                )
                print(f"RRRcorpus_results:{corpus_results}.....{vector_distance_threshold}.........")
                # Add corpus info to the results
                if corpus_results["status"] == "success":
                    results = corpus_results.get("results", [])
                    corpus_specific_results = []
                    
                    for result in results:
                        # Add citation and source information
                        result["corpus_id"] = corpus_id
                        result["corpus_name"] = corpus_name
                        result["citation"] = f"[Source: {corpus_name} ({corpus_id})]"
                        
                        # Add source file information if available
                        if "source_uri" in result and result["source_uri"]:
                            source_path = result["source_uri"]
                            file_name = source_path.split("/")[-1] if "/" in source_path else source_path
                            result["citation"] += f" File: {file_name}"
                        
                        corpus_specific_results.append(result)
                        all_results.append(result)
                    
                    # Save results for this corpus
                    if corpus_specific_results:
                        corpus_results_map[corpus_name] = {
                            "corpus_id": corpus_id,
                            "corpus_name": corpus_name,
                            "results": corpus_specific_results,
                            "count": len(corpus_specific_results)
                        }
                        searched_corpora.append(corpus_name)
        
        # Sort all results by relevance score (if available)
        all_results.sort(
            key=lambda x: x.get("relevance_score", 0) if x.get("relevance_score") is not None else 0,
            reverse=True
        )
        
        # Format citations summary
        citations_summary = []
        for corpus_name in searched_corpora:
            corpus_data = corpus_results_map[corpus_name]
            citations_summary.append(
                f"{corpus_name} ({corpus_data['corpus_id']}): {corpus_data['count']} results"
            )
        
        return {
            "status": "success",
            "results": all_results,
            "corpus_results": corpus_results_map,
            "searched_corpora": searched_corpora,
            "citations_summary": citations_summary,
            "count": len(all_results),
            "query": query_text,
            "message": f"Found {len(all_results)} results for query '{query_text}' across {len(searched_corpora)} corpora",
            "citation_note": "Each result includes a citation indicating its source corpus and file."
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "message": f"Failed to search all corpora: {str(e)}"
        }
    
def list_rag_corpora() -> Dict[str, Any]:
    """
    Lists all RAG corpora in the current project and location.
    
    Returns:
        A dictionary containing the list of corpora:
        - status: "success" or "error"
        - corpora: List of corpus objects with id, name, and display_name
        - count: Number of corpora found
        - error_message: Present only if an error occurred
    """
    try:
        PROJECT_ID = os.getenv("PROJECT_ID")
        LOCATION = os.getenv("LOCATION")
        gcp_credentials_path = os.getenv("gcp_credentials_path")
        credentials = Credentials.from_service_account_file(gcp_credentials_path)
        vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)
        corpora = rag.list_corpora()
        
        corpus_list = []
        for corpus in corpora:
            corpus_id = corpus.name.split('/')[-1]
            
            # Get corpus status
            status = None
            if hasattr(corpus, "corpus_status") and hasattr(corpus.corpus_status, "state"):
                status = corpus.corpus_status.state
            elif hasattr(corpus, "corpusStatus") and hasattr(corpus.corpusStatus, "state"):
                status = corpus.corpusStatus.state
            
            corpus_list.append({
                "id": corpus_id,
                "name": corpus.name,
                "display_name": corpus.display_name,
                "description": corpus.description if hasattr(corpus, "description") else None,
                "status": status
            })
        return {
            "status": "success",
            "corpora": corpus_list,
            "count": len(corpus_list),
            "message": f"Found {len(corpus_list)} RAG corpora"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "message": f"Failed to list RAG corpora: {str(e)}"
        }
    
def query_rag_corpus(
    corpus_id: str,
    query_text: str,
    top_k: Optional[int] = None,
    vector_distance_threshold: Optional[float] = None
) -> Dict[str, Any]:
    """
    Directly queries a RAG corpus using the Vertex AI RAG API.
    
    Args:
        corpus_id: The ID of the corpus to query
        query_text: The search query text
        top_k: Maximum number of results to return (default: 10)
        vector_distance_threshold: Threshold for vector similarity (default: 0.5)
        
    Returns:
        A dictionary containing the query results
    """
    
    if top_k is None:
        top_k = 2
        print(f"RRtop_k: {top_k}...............")
    if vector_distance_threshold is None:
        vector_distance_threshold = 0.5
        print(f"RRvector_distance_threshold: {vector_distance_threshold}...............")
    # Ensure types are correct for downstream API
    try:
        top_k = int(top_k)
    except Exception:
        top_k = 2
    try:
        vector_distance_threshold = float(vector_distance_threshold)
    except Exception:
        vector_distance_threshold = 0.5
    try:
        PROJECT_ID = os.getenv("PROJECT_ID")
        LOCATION = os.getenv("LOCATION")
        # Construct full corpus resource path
        corpus_path = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{corpus_id}"
        
        # Create the resource config
        rag_resource = rag.RagResource(rag_corpus=corpus_path)
        
        # Configure retrieval parameters
        retrieval_config = rag.RagRetrievalConfig(
            top_k=top_k,
            filter=rag.utils.resources.Filter(vector_distance_threshold=vector_distance_threshold)
        )
        
        # Execute the query directly using the API
        response = rag.retrieval_query(
            rag_resources=[rag_resource],
            text=query_text,
            rag_retrieval_config=retrieval_config
        )
        
        # Process the results
        results = []
        if hasattr(response, "contexts"):
            # Handle different response structures
            contexts = response.contexts
            if hasattr(contexts, "contexts"):
                contexts = contexts.contexts
            
            # Extract text and metadata from each context
            for context in contexts:
                result = {
                    "text": context.text if hasattr(context, "text") else "",
                    "source_uri": context.source_uri if hasattr(context, "source_uri") else None,
                    "relevance_score": context.relevance_score if hasattr(context, "relevance_score") else None
                }
                results.append(result)
        
        return {
            "status": "success",
            "corpus_id": corpus_id,
            "results": results,
            "count": len(results),
            "query": query_text,
            "message": f"Found {len(results)} results for query: '{query_text}'"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "corpus_id": corpus_id,
            "error_message": str(e),
            "message": f"Failed to query corpus: {str(e)}"
        }