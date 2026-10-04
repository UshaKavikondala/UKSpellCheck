from dotenv import load_dotenv; load_dotenv()
from my_spellchecker.state import PipelineState
from my_spellchecker.agents.spellcheck_agent import SpellcheckAgent

s = PipelineState(input_text="She go to the libary yesterday.")
s = SpellcheckAgent().run(s)
print(s.spelling_issues, s.total_tokens, s.statuses)