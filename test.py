import torch

if torch.cuda.is_available():
  print("PyTorch is using GPU")
else:
  print("PyTorch is using CPU")