from langchain_core.messages import HumanMessage

from app.supervisor import supervisor_graph


question = input("\nAsk FinGuard AI: ")

result = supervisor_graph.invoke({
    "messages": [
        HumanMessage(content=question)
    ]
})

print("\nFinal Answer:\n")
print(result["result"])