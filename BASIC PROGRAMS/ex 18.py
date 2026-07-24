from transformers import BertTokenizer, BertModel

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

model = BertModel.from_pretrained("bert-base-uncased")

s1 = tokenizer("The cat is sleeping.", return_tensors="pt")

s2 = tokenizer("A kitten is resting.", return_tensors="pt")

e1 = model(**s1).last_hidden_state.mean(dim=1)

e2 = model(**s2).last_hidden_state.mean(dim=1)

print("Embedding 1 Shape:", e1.shape)

print("Embedding 2 Shape:", e2.shape)
