# backend/app/utils/metrics.py

from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

# Use a dedicated registry so we control exactly what’s exposed
registry = CollectorRegistry()

# Counters
CACHE_HITS = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["endpoint"],
    registry=registry
)
CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["endpoint"],
    registry=registry
)
LLM_CALLS = Counter(
    "llm_calls_total",
    "Total LLM calls",
    ["endpoint"],
    registry=registry
)

# Request latency histogram
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    ["endpoint", "method"],
    registry=registry
)

def metrics_response():
    data = generate_latest(registry)
    return data, CONTENT_TYPE_LATEST
