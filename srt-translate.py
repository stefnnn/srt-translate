#!/usr/bin/env python
#
# Auto-translate SRT subtitle files using OpenAI's API

import argparse
import dotenv
import pysrt
import openai
import os
import tqdm

SOURCE_LOCALE = 'en'
TARGET_LOCALE = 'de'
MOVIE = 'A movie'
SPECS = 'in a fitting language'
BATCH_SIZE = 50
GPT_MODEL = 'gpt-4o'
SEPARATOR = '\n***\n'

dotenv.load_dotenv()
openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.Client()
  

def parse_args():
  parser = argparse.ArgumentParser(prog='srt_translate.py', description='Auto-Translate SRT subtitle files')
  parser.add_argument('--input', '-i', type=str, help='Input SRT file', required=True)
  parser.add_argument('--output', '-o', type=str, help='Translated SRT file to write', default=None)
  parser.add_argument('--source', '-s', type=str, help='Source locale', default=SOURCE_LOCALE)
  parser.add_argument('--target', '-t', type=str, help='Target locale', required=True)
  parser.add_argument('--batch_size', type=int, help='Batch size', default=BATCH_SIZE)
  parser.add_argument('--model', type=str, help='OpenAI model', default=GPT_MODEL)
  parser.add_argument('--movie', '-m', type=str, help='Movie name', default=MOVIE)
  parser.add_argument('--specs', type=str, help='Movie specs', default=SPECS)
  return parser.parse_args()

def construct_prompt(args, text):
  return f'Translate the following subtitle dialogue from the movie "{args.movie}" {args.specs} ' + \
    'from "{args.source}" to "{args.target}". Start always right away with the translation and keep ' + \
    'the dialogue separators with three stars:\n\n' + text

def openai_instruct(instruction, model):
  response = client.chat.completions.create(
    model=model, messages=[ {"role": "user", "content": instruction} ]
  )
  return response.choices[0].message.content.strip()

def srt_translate(srt_input, srt_output, args):
  subs = pysrt.open(srt_input)
  batched_subs = [subs[i:i + args.batch_size] for i in range(0, len(subs), args.batch_size)]

  for batch in tqdm.tqdm(batched_subs):
      batch_text = SEPARATOR.join([sub.text for sub in batch])
      instruction = construct_prompt(args, batch_text)
      translated_batch = openai_instruct(instruction, args.model)
      
      for i, sub in enumerate(batch):
          try:
              sub.text = translated_batch.split(SEPARATOR)[i]
          except:
              pass

  subs.save(srt_output)

if __name__ == '__main__':
  args = parse_args()
  srt_input = args.input
  srt_output = args.output or srt_input.replace('.srt', f'_{args.target}.srt')

  srt_translate(srt_input, srt_output, args)