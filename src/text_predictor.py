from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

class TextPredictor:
    def __init__(self):
        # Initialize GPT-2 model for next-word prediction
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.model.eval()
        
        # Initialize Trie for autocomplete
        self.trie = self.Trie()
        self.load_word_list('static/wordlists/google-10000-english-no-swears.txt')

    class TrieNode:
        def __init__(self):
            self.children = {}
            self.is_end_of_word = False

    class Trie:
        def __init__(self):
            self.root = TextPredictor.TrieNode()

        def insert(self, word):
            node = self.root
            for char in word.lower():
                node = node.children.setdefault(char, TextPredictor.TrieNode())
            node.is_end_of_word = True

        def _dfs(self, node, prefix, results):
            if node.is_end_of_word:
                results.append(prefix)
            for char, child in node.children.items():
                self._dfs(child, prefix + char, results)

        def autocomplete(self, prefix, max_results=3):
            node = self.root
            for char in prefix.lower():
                if char in node.children:
                    node = node.children[char]
                else:
                    return []
            results = []
            self._dfs(node, prefix, results)
            return results[:max_results]

    def load_word_list(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                word = line.strip()
                if word:
                    self.trie.insert(word)

    def predict_next_words(self, prompt, top_k=3):
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model(input_ids)
            next_token_logits = outputs.logits[:, -1, :]
        top_k_probs = torch.topk(next_token_logits, k=top_k, dim=-1)
        top_k_ids = top_k_probs.indices[0].tolist()
        suggestions = [self.tokenizer.decode([token_id]).strip() for token_id in top_k_ids]
        return suggestions

    def get_suggestions(self, text_buffer):
        words = text_buffer.strip().split()
        if not words:
            return []
        last_word = words[-1]
        if text_buffer.endswith(' '):
            # Last word is complete; predict next word
            return self.predict_next_words(text_buffer.strip())
        else:
            # Last word is incomplete; suggest completions
            return self.trie.autocomplete(last_word)