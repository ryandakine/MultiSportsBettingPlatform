    async def _invoke_remote_agent(self, agent_info, user_query) -> Optional[Dict[str, Any]]:
        """
        Invoke an agent on a remote HeadAgent instance via HTTP.
        
        Args:
            agent_info: AgentInfo object with instance_id
            user_query: UserQuery object
        
        Returns:
            Prediction dict or None if failed
        """
        try:
            import httpx
            
            # In production, use service discovery or config to get instance URLs
            # For now, assume instances are accessible at known ports/hosts
            # This is a simplified implementation
            
            # TODO: Implement proper service discovery
            # For now, just log that remote invocation would happen
            logger.info(f"Would invoke agent on instance {agent_info.instance_id} for {agent_info.sport}")
            
            # Placeholder for actual HTTP call
            # In real implementation:
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(
            #         f"http://{instance_url}/api/v1/agents/query",
            #         json={
            #             "sport": agent_info.sport,
            #             "query_text": user_query.query_text,
            #             "user_id": user_query.user_id,
            #             "preferences": user_query.preferences
            #         }
            #     )
            #     return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Remote agent invocation failed: {e}")
            return None
