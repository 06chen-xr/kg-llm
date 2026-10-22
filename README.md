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

## Related Publications

This repository is associated with the following peer-reviewed research publications on LLM- and RAG-based knowledge graph construction:

### 1. A Self-Improving, RAG-Enhanced Framework for Automatic Knowledge Graph Construction from Climate Event News

**Authors:** Xiaorui Chen, Haiyan Hao  
**Published in:** Proceedings of the 22nd International ISCRAM Conference (ISCRAM 2025)  
**DOI:** [10.59297/wjmsp389](https://doi.org/10.59297/wjmsp389)  
**Paper:** [Official Publication](https://ojs.iscram.org/index.php/Proceedings/article/view/154)

This study proposes a RAG-enhanced, self-improving framework for extracting entities and relationships from climate event news. It explores iterative refinement and prompt engineering to improve the accuracy and reliability of automatically constructed knowledge graphs.

### 2. Uncovering Compound Urban Crises with Large Language Model-Assisted Knowledge Graph Construction

**Authors:** Haiyan Hao, Xiaorui Chen, Yudi Chen, Nan Li  
**Published in:** International Journal of Disaster Risk Reduction, Volume 127, Article 105669 (2025)  
**DOI:** [10.1016/j.ijdrr.2025.105669](https://doi.org/10.1016/j.ijdrr.2025.105669)  
**Paper:** [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2212420925004935)

This study extends LLM-assisted knowledge graph construction to the analysis of compound urban crises, combining RAG, prompt engineering, and iterative self-refinement to identify relationships among interconnected crisis events.

### Research Context

KG-LLM provides research-oriented implementations and experimental utilities related to these studies, including LLM-based entity extraction, retrieval augmentation, prompt comparison, and structured knowledge graph generation.


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
