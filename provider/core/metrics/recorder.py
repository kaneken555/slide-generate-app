def record(provider:str, metric:str, value:float, labels:dict|None=None):
    # 実運用: Prometheus/OTelにpush。ここではprintで代替。
    print(f"[metrics] {provider}.{metric}={value} {labels or {}}")
