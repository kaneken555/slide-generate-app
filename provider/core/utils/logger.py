def log(provider:str, event:str, **kv):
    print(f"[{provider}] {event} " + " ".join(f"{k}={v}" for k,v in kv.items()))
