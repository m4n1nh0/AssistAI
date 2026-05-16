class SimulatedMCPClient:
    def get_ticket_status(self, ticket_id: str) -> dict[str, str]:
        return {
            "ticket_id": ticket_id,
            "status": "em andamento",
            "last_update": "Chamado encaminhado para equipe de suporte.",
        }
