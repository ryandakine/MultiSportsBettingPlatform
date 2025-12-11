import asyncio
import logging
from src.agents.head_agent import HeadAgent, SportType
from src.agents.sub_agents.baseball_agent import BaseballAgent
from src.agents.sub_agents.basketball_agent import BasketballAgent
from src.agents.sub_agents.football_agent import FootballAgent
from src.agents.sub_agents.hockey_agent import HockeyAgent

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_autonomous():
    print("🧪 Testing Autonomous Features (Multi-Sport)...")
    
    # Initialize Head Agent
    head_agent = HeadAgent()
    
    # Register all agents
    await head_agent.register_sub_agent(SportType.BASEBALL, BaseballAgent())
    await head_agent.register_sub_agent(SportType.BASKETBALL, BasketballAgent())
    await head_agent.register_sub_agent(SportType.FOOTBALL, FootballAgent())
    await head_agent.register_sub_agent(SportType.HOCKEY, HockeyAgent())
    
    print("\nAttempting to scan market...")
    try:
        await head_agent.scan_market()
        print("\n✅ Market scan completed without error!")
    except Exception as e:
        print(f"\n❌ Market scan failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_autonomous())
