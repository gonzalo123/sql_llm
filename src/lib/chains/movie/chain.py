import logging
from langchain_core.messages import SystemMessage, HumanMessage

from .prompts import PROMPT

logger = logging.getLogger(__name__)


class MovieChain:

    def __init__(self, llm):
        self.llm = llm

        self.prompt = SystemMessage(content=PROMPT)

    def get_sql(self, q: str):
        user_message = HumanMessage(content=q)
        try:
            ai_msg = self.llm.invoke([self.prompt, user_message])
            output_message = ai_msg.content if not isinstance(ai_msg, str) else ai_msg

            return output_message
        except Exception as e:
            logger.error(f"Error during question processing: {e}")
