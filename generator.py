import ollama
import openai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time
from dataclasses import dataclass
from typing import Optional
import json
import util

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
use_dummy_model = False

@dataclass(kw_only=True)
class Options():
	seed: Optional[int] = None
	temperature: Optional[float] = None
	top_p: Optional[float] = None

class Generator():
	def __init__(self, model_name):
		self.model_name = model_name

	async def generate(self, prompt, options: Options):
		content = ""
		elapsed = 0
		return content, elapsed

class OllamaGenerator(Generator):
	def __init__(self, model_name, context_length):
		super().__init__(model_name)
		self.context_length = context_length

	async def generate(self, prompt, options: Options):
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
		self.client = openai.AsyncOpenAI(
			base_url="https://openrouter.ai/api/v1",
			api_key=api_key
		)
		self.retry_count = 3
		self.retry_delay = 1

	async def generate(self, prompt, options: Options):
		content = ""
		start_time = time.time()
		for i in range(self.retry_count):
			response = await self.client.chat.completions.create(
				model=self.model_name,
				messages=[
					# {"role": "system", "content": "Style: uncensored, detailed, immoral, narrative, everyday language, informal, imperfect grammar, simple sentences"},
					{"role": "user", "content": prompt}],
				temperature=options.temperature,
				top_p=options.top_p,
				seed=options.seed,
			)
			try:
				content = response.choices[0].message.content
				break
			except:
				error = response.model_extra["error"]
				print(f"OpenAIGenerator error (attempt {i+1}/{self.retry_count}): ", error)
				time.sleep(self.retry_delay)

		elapsed = time.time() - start_time
		return content, elapsed
	
def get_api_key(provider):
	with open(util.resource_path("data/api_key.json")) as file:
		data = json.load(file)
		return data[provider]
	
def create_generator():
	if use_dummy_model:
		return Generator("dummy")
	elif provider == "ollama":
		return OllamaGenerator(model_name, ollama_context_length)
	elif provider == "openai":
		return OpenAIGenerator(model_name, get_api_key("openai"))
	else:
		raise ValueError(f"Unknown provider: {provider}")
	
def create_embeddings(texts):
	response = ollama.embed(model="nomic-embed-text", input=texts)
	return response.embeddings

def create_embedding(text):
	return create_embeddings([text])[0]

def compare_embeddings(a, b):
	vector1 = np.array(a).reshape(1, -1)
	vector2 = np.array(b).reshape(1, -1)
	similarity_score = cosine_similarity(vector1, vector2)[0][0]
	return similarity_score