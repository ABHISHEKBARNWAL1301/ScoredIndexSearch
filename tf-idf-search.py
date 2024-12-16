import collections
import math
import os
import re
import binascii
import redis
import random

NON_WORDS = re.compile("[^a-z0-9' ]")  # Helps in filtering out unwanted characters (like punctuation or special symbols)

STOP_WORDS = set('''a able about across after all almost also am among
an and any are as at be because been but by can cannot could dear did
do does either else ever every for from get got had has have he her
hers him his how however i if in into is it its just least let like
likely may me might most must my neither no nor not of off often on
only or other our own rather said say says she should since so some
than that the their them then there these they this tis to too twas us
wants was we were what when where which while who whom why will with
would yet you your'''.split())  # Stop words are commonly used words in a language that are often filtered out during text processing because they carry less meaningful information.


class ScoredIndexSearch(object):
    def __init__(self, prefix, host='localhost', port=6379):
        self.prefix = prefix.lower().rstrip(':') + ':'
        self.rclient = redis.Redis(host=host, port=port)  # Create a rclient to our Redis server.
        self.delete_all_keys()

        # Add multiple indexed items using the generated random sentences
        random_sentences = ScoredIndexSearch.generate_random_sentences( 2000)  # Generate 20 random sentences
        for i, content in enumerate(random_sentences, start=1): 
            print(f"Adding document {i} to the index") 
            self.add_indexed_item(i, content)

    @staticmethod
    def get_index_keys(content, add=True):
        # Very simple word-based parser. We skip stop words and single character words.
        words = NON_WORDS.sub(' ', content.lower()).split()
        words = [word.strip("'") for word in words]
        words = [word for word in words if word not in STOP_WORDS and len(word) > 1]

        if not add:
            return words

        # Calculate the TF portion of TF/IDF.
        counts = collections.defaultdict(float)
        for word in words:
            counts[word] += 1
        wordcount = len(words)
        tf = {word: count / wordcount for word, count in counts.items()}  # Changed to items()
        return tf

    def _handle_content(self, id, content, add=True):
        # Get the keys we want to index.
        keys = self.get_index_keys(content)
        prefix = self.prefix

        # Use a non-transactional pipeline here to improve performance.
        pipe = self.rclient.pipeline(False)

        if add:
            pipe.sadd(prefix + 'indexed:', id)
            # Store the document content in Redis
            pipe.set(prefix + f'doc:{id}', content)
            for key, value in keys.items():  # Changed to items()
                pipe.zadd(prefix + key, {id: value})  # zadd expects a dict of {id: value}
        else:
            pipe.srem(prefix + 'indexed:', id)
            # Remove the document content from Redis
            pipe.delete(prefix + f'doc:{id}')
            for key in keys:
                pipe.zrem(prefix + key, id)

        # Execute the insertion/removal.
        pipe.execute()

        return len(keys)

    def add_indexed_item(self, id, content):
        return self._handle_content(id, content, add=True)

    def remove_indexed_item(self, id, content):
        return self._handle_content(id, content, add=False)

    def add_multiple_items(self, items):
        """Add multiple indexed items. Items should be a list of tuples (id, content)."""
        for id, content in items:
            self.add_indexed_item(id, content)

    def search(self, query_string, offset=0, count=5):  # Limit to 5 results
        def idf(count):
            # Calculate the IDF for this particular count
            if not count:
                return 0
            return max(math.log(total_docs / count, 2), 0)

        # Get our search terms just like we did earlier...
        keys = [self.prefix + key for key in self.get_index_keys(query_string, False)]

        if not keys:
            return [], 0

        total_docs = max(self.rclient.scard(self.prefix + 'indexed:'), 1)

        # Get our document frequency values...
        pipe = self.rclient.pipeline(False)
        for key in keys:
            pipe.zcard(key)
        sizes = pipe.execute()

        # Calculate the inverse document frequencies...
        idfs = list(map(idf, sizes))

        # And generate the weight dictionary for passing to zunionstore.
        weights = {key: idfv for key, size, idfv in zip(keys, sizes, idfs) if size}

        if not weights:
            return [], 0

        # Generate a temporary result storage key
        temp_key = self.prefix + 'temp:' + binascii.hexlify(os.urandom(8)).decode()

        try:
            # Perform the union to combine the scores.
            known = self.rclient.zunionstore(temp_key, weights)
            # Get the results.
            ids = self.rclient.zrevrange(temp_key, offset, offset + count - 1, withscores=True)
        finally:
            # Clean up after ourselves.
            self.rclient.delete(temp_key)

        # Retrieve the actual document content based on IDs
        documents = [self.rclient.get(self.prefix + f'doc:{doc_id.decode()}').decode() for doc_id, _ in ids]
        return documents

    def generate_random_sentences(num_sentences):
        subjects = ["The cat", "A dog", "The man", "A woman", "The teacher", "The student"]
        verbs = ["jumps", "runs", "sits", "sleeps", "eats", "reads"]
        objects = ["on the mat", "in the garden", "at the park", "with a book", "under the tree", "in the house"]
        
        sentences = []
        for _ in range(num_sentences):
            sentence = f"{random.choice(subjects)} {random.choice(verbs)} {random.choice(objects)}."
            sentences.append(sentence)
        return sentences
    
    def delete_all_keys(self):
        keys_to_delete = self.rclient.keys(self.prefix + '*')
        if keys_to_delete:
            self.rclient.delete(*keys_to_delete)

if __name__ == '__main__':
    # Initialize the search with a Redis rclient (default: localhost and port 6379)
    t = ScoredIndexSearch('unittest', host='localhost', port=6379)


    # Main loop to take input and search
    while True:
        query = input("Enter your search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        result = t.search(query)
        print("Search results:")
        for doc in result:
            print(f"- {doc}")



