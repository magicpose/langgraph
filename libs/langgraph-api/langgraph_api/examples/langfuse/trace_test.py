from langfuse import Langfuse
import os

# Set environment variables
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-c80344d8-e19b-4c4a-8925-2f1c95ed3344"
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-ffbee855-d174-4b13-aa8b-2dd6715cbfda"
os.environ["LANGFUSE_HOST"] = "http://10.1.3.122:3005"


# Create Langfuse client
langfuse = Langfuse()

trace = langfuse.trace(
    metadata={"tracemetakey": "tracemetavalue"},
    session_id="test-session"
)

print(trace.get_trace_url())
trace = langfuse.trace(name="llm-feature")
retrieval = trace.span(name="retrieval")
retrieval.generation(name="query-creation")
retrieval.span(name="vector-db-search")
retrieval.event(name="db-summary")
trace.generation(name="user-output")

# The SDK executes network requests in the background.
# To ensure that all requests are sent before the process exits, call flush()
# Not necessary in long-running production code
langfuse.flush()
