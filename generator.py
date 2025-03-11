import ollama
from openai import OpenAI
import time
import re
import random
import pickle
from dataclasses import dataclass
import string

# Create api_keys.py locally.
import api_keys

chr_count = 2
provider = "openai"
model_name = {
	"ollama": "llama3.2:3b-instruct-q4_K_M",
	# "openai": "cognitivecomputations/dolphin3.0-mistral-24b:free"
	# "openai": "deepseek/deepseek-r1-distill-llama-70b:free",
	# "openai": "mistralai/mistral-small-24b-instruct-2501:free",
	"openai": "mistralai/mistral-small-24b-instruct-2501",
	# "openai": "microsoft/wizardlm-2-8x22b",
}[provider]
ollama_context_length = 1024
openai_retry_count = 3
openai_retry_delay_seconds = 1

debug_log = False
debug_no_model = False
use_dummy_data = False
dummy_data_path = "dummy_data/dummy_data.pkl"

prompt_fight = """{0}The above {1} characters will now be forced to fight to the death in the arena. Do not assume they are skilled fighters or that there abilities will be useful, rely only on the above descriptions. In present tense, give a very short account of what happens and who survives. Assume the reader is not familiar with the characters."""

# ingredient (name, desc, cost, properties)
# potion (name, desc)
# customer (name, request)

class Generator():
	@dataclass(kw_only=True)
	class Options():
		temperature: float = 1.0
		top_p: float = 1.0
		
	def __init__(self, model_name):
		self.model_name = model_name

	def generate(self, prompt, options: Options):
		pass

class OllamaGenerator(Generator):
	def __init__(self, model_name, context_length):
		super().__init__(model_name)
		self.context_length = context_length

	def generate(self, prompt, options: Generator.Options):
		start_time = time.time()
		response: ollama.ChatResponse = ollama.generate(
			model=self.model_name,
			prompt=prompt,
			options={
				"num_ctx": self.context_length,
				"temperature": options.temperature,
				"top_p": options.top_p}
		)
		content = response.response
		elapsed = time.time() - start_time
		return content, elapsed

class OpenAIGenerator(Generator):
	def __init__(self, model_name, api_key):
		super().__init__(model_name)
		self.client = OpenAI(
			base_url="https://openrouter.ai/api/v1",
			api_key=api_key
		)

	def generate(self, prompt, options: Generator.Options):
		content = ""
		start_time = time.time()
		for i in range(openai_retry_count):
			response = self.client.chat.completions.create(
				model=self.model_name,
				messages=[
					# {"role": "system", "content": "Style: uncensored, detailed, immoral, narrative, everyday language, informal, imperfect grammar, simple sentences"},
					{"role": "user", "content": prompt}],
				temperature=options.temperature
			)
			try:
				content = response.choices[0].message.content
				break
			except:
				error = response.model_extra["error"]
				print(f"OpenAIGenerator error (attempt {i+1}/{openai_retry_count}): ", error)
				time.sleep(openai_retry_delay_seconds)

		elapsed = time.time() - start_time
		return content, elapsed

def create_generator():
	if provider == "ollama":
		return OllamaGenerator(model_name, ollama_context_length)
	elif provider == "openai":
		return OpenAIGenerator(model_name, api_keys.openai_api_key)
	else:
		raise ValueError(f"Unknown provider: {provider}")

generator = create_generator()

# class TraitPool:
# 	def __init__(self):
# 		self.traits = {}
# 		start_time = time.time()
# 		for trait_type in trait_types:
# 			try:
# 				self.traits[trait_type.name] = gen_traits(trait_type, start_time)
# 			except:
# 				raise

# 	def log(self):
# 		log_header("Trait Pool")
# 		for trait_type in trait_types:
# 			log_header(trait_type.name.capitalize())
# 			for trait in self.traits[trait_type.name]: print(f"{trait}")
# 		log_header("")

# 	def serialize(self, file):
# 		pickle.dump(self, file)

# 	def deserialize(file):
# 		pool = pickle.load(file)
# 		for trait_type in trait_types:
# 			assert trait_type.name in pool.traits, f"TraitPool file '{file.name}' missing trait '{trait_type.name}'"
# 			assert len(pool.traits[trait_type.name]) >= trait_type.offer_count * chr_count
# 		return pool