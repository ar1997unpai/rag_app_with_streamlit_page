from pathlib import Path
import sys

if __package__:
    from .promptResponse import post_request
    from .rag import retrieve_context
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend.promptResponse import post_request
    from backend.rag import retrieve_context


def main():
    user_input = input("What would you like help with? ").strip()

    if not user_input:
        print("Please enter a question.")
        return

    documents = retrieve_context(user_input)

    context = "\n\n".join(
        f"Source: {doc['source']}\n{doc['text']}"
        for doc in documents
    )

    if not context:
        context = "No relevant documents were retrieved."

    result = post_request(user_input, context)

    print("\nAnswer:")
    print(result["message"]["content"])

    if documents:
        print("\nSources:")
        for source in sorted(set(doc["source"] for doc in documents)):
            print(f"- {source}")


if __name__ == "__main__":
    main()
