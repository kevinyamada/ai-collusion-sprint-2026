def trim_generated(tokens,eos_ids):
    """Remove batch padding after the first generation stop token, keeping EOS itself."""
    for i,t in enumerate(tokens):
        if t in eos_ids:return tokens[:i+1]
    return tokens
