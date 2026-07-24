from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

text = "Artificial Intelligence"

tokens = tokenizer.tokenize(text)

ids = tokenizer.convert_tokens_to_ids(tokens)

print(tokens)

print(ids)
