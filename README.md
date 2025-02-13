# KG-LLM: Knowledge Graph Recognition Framework with RAG and Large Language Models

## Overview

This repository provides a framework that integrates Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) to enhance knowledge graph recognition. The project focuses on extracting structured knowledge from unstructured text using LLMs and comparing different prompt designs to optimize performance.

Key Features
Module-based Architecture: The core module.py script serves as the framework for LLM-based knowledge graph extraction.
Retrieval-Augmented Generation (RAG): Enhances entity extraction and knowledge graph construction using pre-indexed embeddings.
Prompt Comparison: Evaluates different prompt structures to improve knowledge extraction accuracy (result_compare.py).
Entity Embeddings: Precomputed vector representations of knowledge database entities (entity_embeddings.json).
Data Processing: Supports multiple data formats (data.txt, test_data.txt, graph_database_export.xlsx, news_subset.xlsx).
Knowledge Graph Export: Converts extracted knowledge into structured formats (kg_toexcel.py).

## Key Features

- **Module-based Architecture**:  
  The core `module.py` script serves as the framework for LLM-based knowledge graph extraction.

- **Retrieval-Augmented Generation (RAG)**:  
  Enhances entity extraction and knowledge graph construction using pre-indexed embeddings.

- **Prompt Comparison**:  
  Evaluates different prompt structures to improve knowledge extraction accuracy (`result_compare.py`).

- **Entity Embeddings**:  
  Precomputed vector representations of knowledge database entities (`entity_embeddings.json`).

- **Data Processing**:  
  Supports multiple data formats (`data.txt`, `test_data.txt`, `graph_database_export.xlsx`, `news_subset.xlsx`).

- **Knowledge Graph Export**:  
  Converts extracted knowledge into structured formats (`kg_toexcel.py`).

## Project Structure

| File | Description |
|------|------------|
| **`module.py`** | Core framework for integrating LLMs with RAG-based knowledge graph recognition. |
| **`result_compare.py`** | Script for comparing different prompt structures and their effectiveness in knowledge graph extraction. |
| **`entity_embeddings.json`** | Precomputed vector embeddings of knowledge entities for retrieval augmentation. |
| `data.txt`, `test_data.txt` | Input text data for knowledge extraction. |
| `graph_database_export.xlsx` | Exported structured knowledge graph in Excel format. |
| `news_subset.xlsx` | Subset of news articles used for testing and benchmarking. |
| `data_toKA.py` | Preprocessing script to transform raw data into a format suitable for knowledge extraction. |
| `kg_toexcel.py` | Converts extracted knowledge into Excel format for analysis. |
| `requirements.txt` | Dependencies required for running the project. |


## Getting Started

### **Installation**

1.**Clone the repository**:
   `bash
   git clone https://github.com/your-repo/kg-llm.git
   cd kg-llm`

2.**Install dependencies**:

```pip install -r requirements.txt```



### **Usage**
1.**Run the core module**:

```python module.py```

This will process input text and extract structured knowledge.

2.**Compare prompt performances**:

```python result_compare.py```

This evaluates different prompt designs for knowledge graph extraction.

3.**Export knowledge graph**:

```python kg_toexcel.py```

Saves extracted entities and relationships in an Excel sheet.

## Future Improvements

- **Introducing Self-Correcting Agent**: Implement an iterative feedback mechanism to refine entity and relationship extraction.
- **Expanding Knowledge Graph Coverage**: Incorporating more diverse datasets.
- **Optimizing Entity Retrieval**: Improving RAG-based retrieval with dynamic embeddings.
