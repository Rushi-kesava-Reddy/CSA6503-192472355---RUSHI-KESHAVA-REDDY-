from transformers import BertTokenizer, GPT2Tokenizer

bert = BertTokenizer.from_pretrained("bert-base-uncased")

gpt2 = GPT2Tokenizer.from_pretrained("gpt2")

text = "Natural Language Processing"

print("BERT:", bert.tokenize(text))

print("GPT-2:", gpt2.tokenize(text))
