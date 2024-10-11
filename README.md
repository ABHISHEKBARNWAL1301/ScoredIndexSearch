# README for ScoredIndexSearch Project

## Overview

The **ScoredIndexSearch** project implements a simple TF/IDF indexing and search algorithm using Redis as a datastore. It allows users to add documents, index them, and perform efficient searches based on term relevance.

### Features

- **TF/IDF Scoring**: Utilizes Term Frequency (TF) and Inverse Document Frequency (IDF) to rank documents based on the relevance of search terms.

   ![image](https://github.com/user-attachments/assets/cd667aa6-cd49-41ef-a429-8cd065488a1f)

- **Redis Integration**: Leverages Redis for fast data storage and retrieval, making it suitable for real-time search applications.
- **Random Document Generation**: Automatically generates random sentences to populate the index for testing purposes.
- **Flexible Search Functionality**: Allows users to search for terms and retrieve relevant documents with scores.
- **Dynamic Document Management**: Supports adding, removing, and searching indexed items dynamically.


## Example Run

To see the project in action:

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>

2. **Install Dependencies**:
    Make sure you have Redis installed and running. You can install the redis Python package using pip:

    ```
    pip install redis
    ```

3. **Run the Application**:
    Execute the script:
    ```
    python redis-search.py
    ```

    Perform a Search:
    When prompted, enter your search query. For example:

    ```
    Enter your search query (or 'exit' to quit): world
    ```

    View Results:
    The application will display relevant documents based on your query.


## Future Plans
   - Enhanced Query Processing: Implement more features such as phrase searching, Synonyms and Stemming.
   - Performance Optimization: Explore caching strategies and other optimizations to improve search speed and efficiency.
   - Sharding: If you're working with large datasets, consider sharding your data across multiple Redis instances to improve performance.
   - Autocomplete Suggestions: Implement an autocomplete feature that suggests queries as users type, enhancing user interaction.







