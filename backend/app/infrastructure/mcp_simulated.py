import re


class SimulatedMCPClient:
    def get_ticket_status(self, message: str) -> dict[str, str] | None:
        match = re.search(r"CHM-\d+", message.upper())
        if not match:
            return None

        ticket_id = match.group(0)
        return {
            "ticket_id": ticket_id,
            "status": "em andamento",
            "last_update": "Chamado encaminhado para a equipe de suporte interno.",
        }


mcp_client = SimulatedMCPClient()
