from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

# Create a dedicated Prometheus registry to control exposed metrics
registry = CollectorRegistry()

# Counter for total cache hits, labeled by endpoint
CACHE_HITS = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    ["endpoint"],
    registry=registry,
)

# Counter for total cache misses, labeled by endpoint
CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total number of cache misses",
    ["endpoint"],
    registry=registry,
)

# Counter for total LLM calls, labeled by endpoint
LLM_CALLS = Counter(
    "llm_calls_total",
    "Total number of LLM calls",
    ["endpoint"],
    registry=registry,
)

# Histogram to track request latency in seconds, labeled by endpoint and HTTP method
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    ["endpoint", "method"],
    registry=registry,
)


def metrics_response():
    """
    Generate an HTTP-compatible Prometheus metrics response.

    Returns:
        A tuple of (metrics data bytes, content type header) for use in FastAPI responses.
    """
    data = generate_latest(registry)  # Serialize registry metrics to Prometheus format
    return data, CONTENT_TYPE_LATEST  # Return payload and correct MIME type
