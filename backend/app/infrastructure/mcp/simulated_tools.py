from dataclasses import dataclass


@dataclass(slots=True)
class ToolResult:
    name: str
    input_payload: dict[str, str]
    output_payload: dict[str, str]
    success: bool


class SimulatedToolRegistry:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.allowed_tools = {"ticket_status"}

    def ticket_status(self, ticket_id: str) -> ToolResult:
        payload = {"ticket_id": ticket_id}
        if not self.enabled:
            return ToolResult(
                name="ticket_status",
                input_payload=payload,
                output_payload={"error": "MCP simulado desabilitado"},
                success=False,
            )

        return ToolResult(
            name="ticket_status",
            input_payload=payload,
            output_payload={
                "ticket_id": ticket_id,
                "status": "em andamento",
                "last_update": "Chamado encaminhado para equipe de suporte.",
            },
            success=True,
        )

