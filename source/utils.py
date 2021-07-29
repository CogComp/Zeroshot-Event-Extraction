import os
import json
import glob
import lxml.etree as et
from nltk.corpus import stopwords
from nltk import word_tokenize, sent_tokenize
from copy import deepcopy
from allennlp.predictors.predictor import Predictor
from pprint import pprint
import torch
import collections
import numpy as np
from itertools import product

bert_type_models = ['bert',
                    'bertl',
					'mbert',
                    'qamr-squad2_bert-l',
                    'qamr_mbert',
                    'qamr_mbert-cased',
                    "squad2_mbert",
					"MLQA_squad2_mbert",
					'elior_bert-lc_mnli',
					'elior_bert_squad2',
                    "elior_bert-lc_mnli_squad2",
					'squad2_elior_bert-lc_mnli',
					'qamr_elior_bert-lc_mnli',
					'qamr-squad2_elior_bert-lc_mnli',
                    'squad2_1sent_bert',
                    'squad2_1sent_roberta',
                    'squad2-s_na+ha_bert',
                    'squad2_ha_bert',
                    ]


def match_bert_span_to_text(pred,
			                bertid_2_goldid,
			                question_len,
			                context_tokens
                            ):
	"""
		Match the predicted bert span to the text in gold context.
		Args:
			pred (:obj:`dict`):
				The prediction dictionary.
			bertid_2_goldid (:obj:`list`):
				The list mapping bert token ids to gold token ids.
			question_len (:obj:`int`):
				The length of the question in bert tokens.
			context_tokens (:obj:`list`):
				The list of gold context tokens.
		"""
	# print("\n")
	# print(pred)
	answer_start, answer_end = pred["span"]

	# null prediction
	if (answer_start, answer_end) == (0, 0):
		return {'span': None,
		        'answer': None,
		        'answer_tokens': None,
		        'confidence': pred["confidence"],
		        "start_logit": pred["start_logit"],
		        "end_logit": pred["end_logit"],
		        }

	# prediction is not in context
	if (answer_start < question_len or answer_end < question_len):
		return None

	bert_span = (answer_start - question_len, answer_end - question_len)  # span in bert tokens

	gold_span = (bertid_2_goldid[bert_span[0]], bertid_2_goldid[bert_span[1]] + 1)  # span in gold tokens

	# span contains invalid tokens
	if (gold_span[0] < 0 or gold_span[1] < 0):
		return None

	answer_tokens = context_tokens[gold_span[0]:gold_span[1]]

	answer = ' '.join(answer_tokens)
	# print(bert_span)
	# print(gold_span)
	# print(answer_tokens)

	return {'span': gold_span,
	        'answer': answer,
	        'answer_tokens': answer_tokens,
	        'confidence': pred["confidence"],
	        "start_logit": pred["start_logit"],
	        "end_logit": pred["end_logit"],
	        }

def postprocess_qa_predictions(input_ids,
                               predictions, # Tuple[np.ndarray, np.ndarray],
							   question_len,
                               version_2_with_negative: bool = False,
                               n_best_size: int = 10,
                               max_answer_length: int = 30,
                               null_score_diff_threshold: float = 0.0,
                               ):
	"""
	Adapted from huggingface utils_qa.py.
	Post-processes the predictions of a question-answering model to convert them to answers that are substrings of the
	original contexts. This is the base postprocessing functions for models that only return start and end logits.
	Args:
		predictions (:obj:`Tuple[np.ndarray, np.ndarray]`):
			The predictions of the model: two arrays containing the start logits and the end logits respectively. Its
			first dimension must match the number of elements of :obj:`features`.
		version_2_with_negative (:obj:`bool`, `optional`, defaults to :obj:`False`):
			Whether or not the underlying dataset contains examples with no answers.
		n_best_size (:obj:`int`, `optional`, defaults to 20):
			The total number of n-best predictions to generate when looking for an answer.
		max_answer_length (:obj:`int`, `optional`, defaults to 30):
			The maximum length of an answer that can be generated. This is needed because the start and end predictions
			are not conditioned on one another.
		null_score_diff_threshold (:obj:`float`, `optional`, defaults to 0):
			The threshold used to select the null answer: if the best answer has a score that is less than the score of
			the null answer minus this threshold, the null answer is selected for this example (note that the score of
			the null answer for an example giving several features is the minimum of the scores for the null answer on
			each feature: all features must be aligned on the fact they `want` to predict a null answer).
			Only useful when :obj:`version_2_with_negative` is :obj:`True`.
		output_dir (:obj:`str`, `optional`):
			If provided, the dictionaries of predictions, n_best predictions (with their scores and logits) and, if
			:obj:`version_2_with_negative=True`, the dictionary of the scores differences between best and null
			answers, are saved in `output_dir`.
		prefix (:obj:`str`, `optional`):
			If provided, the dictionaries mentioned above are saved with `prefix` added to their names.
		is_world_process_zero (:obj:`bool`, `optional`, defaults to :obj:`True`):
			Whether this process is the main process or not (used to determine if logging/saves should be done).
	"""

	prelim_predictions = []

	assert len(predictions) == 2, "`predictions` should be a tuple with two elements (start_logits, end_logits)."
	start_logits, end_logits = predictions
	start_logits = [float(_) for _ in start_logits]
	end_logits = [float(_) for _ in end_logits]

	# Update minimum null prediction.
	null_score = start_logits[0] + end_logits[0]
	null_prediction = {
		"span": (0, 0),
		"answer": "",
		"confidence": null_score,
		"start_logit": start_logits[0],
		"end_logit": end_logits[0],
	}

	# Go through all possibilities for the `n_best_size` greater start and end logits.
	start_indices = np.argsort(start_logits)[-1: -n_best_size - 1: -1].tolist()
	end_indices = np.argsort(end_logits)[-1: -n_best_size - 1: -1].tolist()
	for start_index, end_index in product(start_indices, end_indices):
		# Don't consider out-of-scope answers, either because the indices are out of bounds or correspond
		# to part of the input_ids that are not in the context.

		if start_index >= len(input_ids)-1 or end_index >= len(input_ids)-1 :
			continue

		# Don't add null prediction here.
		if start_index == 0 and end_index == 0:
			continue

		# Don't consider answers with a length that is either < 0 or > max_answer_length.
		if end_index < start_index or end_index - start_index + 1 > max_answer_length:
			continue

		# Answer includes tokens before the context
		if end_index <= question_len or start_index <= question_len:
			continue

		# Answer includes the last special token
		if start_index == len(input_ids) or end_index == len(input_ids):
			continue

		prelim_predictions.append(
			{
				"answer": "non-empty",
				"span": (start_index, end_index),
				"confidence": start_logits[start_index] + end_logits[end_index],
				"start_logit": start_logits[start_index],
				"end_logit": end_logits[end_index],
			}
		)

	if version_2_with_negative:
		# Add the minimum null prediction
		prelim_predictions.append(null_prediction)

	# Only keep the best `n_best_size` predictions.
	all_predictions = sorted(prelim_predictions, key=lambda x: x["confidence"], reverse=True)[:n_best_size]

	# Add back the minimum null prediction if it was removed because of its low score.
	if version_2_with_negative and not any(p["span"] == (0, 0) for p in all_predictions):
		all_predictions.append(null_prediction)

	# Use the offsets to gather the answer text in the original context.
	# for pred in all_predictions:
	# 	span = pred["span"]
	# 	start = span[0]
	# 	end = span[1] + 1
	# 	pred["answer"] = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[start:end]))

	# In the very rare edge case we have not a single non-null prediction, we create a fake prediction to avoid
	# failure.
	if len(all_predictions) == 0 or (len(all_predictions) == 1 and all_predictions[0]["answer"] == ""):
		all_predictions.insert(0, {"answer": "empty", "span": (0, 0), "start_logit": 0.0, "end_logit": 0.0, "confidence": 0.0})

	# Compute the softmax of all scores (we do it with numpy to stay independent from torch/tf in this file, using
	# the LogSumExp trick).
	scores = np.array([pred.pop("confidence") for pred in all_predictions])
	exp_scores = np.exp(scores - np.max(scores))
	probs = exp_scores / exp_scores.sum()

	# Include the probabilities in our predictions.
	for prob, pred in zip(probs, all_predictions):
		pred["confidence"] = prob

	return all_predictions, null_prediction

def get_srl_results(instance,
                    predicate_type,
                    srl_dicts,
                    sw,
                    srl_args,
                    srl_model
                    ):
	"""Get the SRL result for one instance. """

	srl_id_results = {}  # verb+nom srl results. Each item stores the result of a predicate. Format: {srl_id: srl_result, ....}
	text_pieces = {}  # pieces of text from the input sentence (e.g. concatenation of V, A0, A1) as the premise. Format: {srl_id: text_piece, ....}
	trg_cands = {}  # trigger candidates. Format: {srl_id: ((span_start, span_end), trigger_text), ....}
	srl2gold_maps = []
	srl_id = 0  # a common key used across srl_id_results, text_pieces, verbs

	if len(srl_dicts) == 2:
		verb_srl_dict, nom_srl_dict = srl_dicts
	else:
		if predicate_type == ['verb']:
			verb_srl_dict = srl_dicts[0]
		if predicate_type == ['nom']:
			nom_srl_dict = srl_dicts[0]

	# SRL
	if 'verb' in predicate_type:  # load verbSRL output
		verb_srl_output, verb_srl2gold = get_verb_srl(verb_srl_dict, instance)  # the entire srl output; mapping from SRL token ids to gold token ids
		verb_srl_tokens, verb_srl_results = verb_srl_output['words'], verb_srl_output['verbs']  # tokens according to SRL tokenization; srl results
		srl2gold_maps.append(verb_srl2gold)
		# get non-stopword verbs
		if not verb_srl_results:
			verb_srl_results = []
		for res in verb_srl_results:
			if set(res['tags']) != {'B-V', 'O'} and res['verb'] not in sw:
				span = [i for i, tag in enumerate(res['tags']) if tag in ['B-V', 'I-V']]
				if span:
					span = (verb_srl2gold[span[0]], verb_srl2gold[span[-1]] + 1)  # map srl ids to gold ids
					text_piece = ' '.join([verb_srl_tokens[i] for i, tag in enumerate(res['tags']) if
					                       overlap(tag, srl_args)])  # get the text piece as the concatenation of the SRL predicate and certain arguments
					text_pieces[srl_id] = text_piece
					trg_cands[srl_id] = (span, res['verb'])
					srl_id_results[srl_id] = res
					srl_id_results[srl_id]['predicate_type'] = 'verb'
					srl_id_results[srl_id]['words'] = verb_srl_output['words']
					srl_id += 1

	if 'nom' in predicate_type:  # load nomSRL output
		nom_srl_output, nom_srl2gold = get_nom_srl(nom_srl_dict, instance)  # the entire srl output; mapping from SRL token ids to gold token ids
		nom_srl_tokens, nom_srl_results = nom_srl_output['words'], nom_srl_output[
			'nominals']  # tokens according to SRL tokenization; srl results
		srl2gold_maps.append(nom_srl2gold)
		# get non-stopword nominals
		if not nom_srl_results:
			nom_srl_results = []
		for res in nom_srl_results:
			if set(res['tags']) != {'O'} and res['nominal'] not in sw:
				span = None
				if srl_model == "celine_old":
					span = res["predicate_index"]
					for pred_id in span:
						res['tags'][pred_id] = "B-V"
				else:
					span = [i for i, tag in enumerate(res['tags']) if tag in ['B-V', 'I-V']]
				if span:
					span = (nom_srl2gold[span[0]], nom_srl2gold[span[-1]] + 1)  # map srl ids to gold ids
					text_piece = ' '.join([nom_srl_tokens[i] for i, tag in enumerate(res['tags']) if
					                       overlap(tag, srl_args)])  # get the text piece as the concatenation of the SRL predicate and certain arguments
					text_pieces[srl_id] = text_piece
					trg_cands[srl_id] = (span, res['nominal'])
					srl_id_results[srl_id] = res
					srl_id_results[srl_id]['predicate_type'] = 'nom'
					srl_id_results[srl_id]['words'] = nom_srl_output['words']
					srl_id += 1

	return srl_id_results, text_pieces, trg_cands, srl2gold_maps

def gold_to_bert_tokens(tokenizer, gold_tokens, EX_QA_model_type):
	"""Tokenize a piece of text using a Huggingface transformers tokenizer, and get a mapping between gold tokens and bert tokens. """
	goldid_2_bertid = []
	if EX_QA_model_type in bert_type_models:
		bert_tokens = []
		bertid_2_goldid = []
		grouped_inputs = []  # input ids to pass to QA model
	else:
		bert_tokens = ['<s>']
		bertid_2_goldid = [-1]
		grouped_inputs = [torch.LongTensor([tokenizer.bos_token_id])]  # input ids to pass to QA model

	for goldid, gold_token in enumerate(gold_tokens):
		goldid_2_bertid.append([])
		if EX_QA_model_type in bert_type_models:
			_tokens_encoded = tokenizer.encode(gold_token, return_tensors="pt", add_special_tokens=False).squeeze(axis=0)
		elif EX_QA_model_type == 'qamr_xlm-roberta':
			_tokens_encoded = tokenizer.encode(gold_token, return_tensors="pt", add_special_tokens=False).squeeze(axis=0)
		else:
			_tokens_encoded = tokenizer.encode(gold_token, add_prefix_space=True, return_tensors="pt", add_special_tokens=False).squeeze(axis=0)
		_tokens = tokenizer.convert_ids_to_tokens(_tokens_encoded.tolist())
		grouped_inputs.append(_tokens_encoded)
		for bert_token in _tokens:
			bert_tokens.append(bert_token)
			bertid_2_goldid.append(goldid)
			goldid_2_bertid[-1].append(len(bertid_2_goldid) - 1)
	if EX_QA_model_type in bert_type_models:
		grouped_inputs.append(torch.LongTensor([tokenizer.sep_token_id]))  # input ids to pass to QA model
		bert_tokens.append('[SEP]')
	else:
		grouped_inputs.append(torch.LongTensor([tokenizer.eos_token_id]))
		bert_tokens.append('</s>')
	bertid_2_goldid.append(-1)
	flattened_inputs = torch.cat(grouped_inputs)
	flattened_inputs = torch.unsqueeze(flattened_inputs, 0)
	return flattened_inputs, bert_tokens, goldid_2_bertid, bertid_2_goldid

def get_gold_map(tokens, gold_tokens):
	"""There is often an inconsistency between arbitrary token ids (e.g. the SRL token ids) and the gold ACE token ids. This method maps arbitrary ids to gold ids.
	
	:param tokens (list): a list of arbitrary tokens.
	:param gold_tokens (list): a list of gold tokens.
	:return (list): a list mapping arbitrary token ids to gold token ids, i.e. tokenid_2_goldid[an_arbitrary_id] would give the corresponding gold id.
	"""
	tokenid_2_goldid = {}
	i, j = -1, -1 # token pointer, gold token pointer
	prefix_i = prefix_j= ''
	len_prefix_i = len_prefix_j = 0
	loop_count = 0
	while i < len(tokens) and j < len(gold_tokens):
		loop_count += 1
		if loop_count >= 1000:
			print(f'Infinite loop:{loop_count}\n{tokens}\n{gold_tokens}\n{prefix_i}\n{prefix_j}')
			break
			# return None
		if prefix_i == '':
			i += 1
			prefix_i += tokens[i]
		if prefix_j == '':
			j += 1
			prefix_j += gold_tokens[j]
		if prefix_i == prefix_j: # matched
			for idx in range(i-len_prefix_i, i+1):
				tokenid_2_goldid[idx] = j # TODO: check if this is the optimal solution
			prefix_i = prefix_j= ''
			len_prefix_i = len_prefix_j = 0
			if i == len(tokens)-1 and j == len(gold_tokens)-1:
				break
		elif prefix_i in prefix_j:
			i += 1
			prefix_i += tokens[i]
			len_prefix_i += 1
		elif prefix_j in prefix_i:
			j += 1
			prefix_j += gold_tokens[j]
			len_prefix_j += 1
	assert [i in tokenid_2_goldid for i in range(len(tokens))]		
	return tokenid_2_goldid

def load_stopwords():
	sw = stopwords.words('english')
	sw += ['said', 'say', 'says', 'saying', 'want', 'wants', 'wanted']
	return sw

def overlap(tag, srl_args):
	"""Checks if a tag is in the set of SRL tags to include in the textpiece.
	
	:param tag (str): a pos tag from SRL output, e.g. 'B-V'.
	:param srl_args (list): a list of SRL tags to include in the textpiece set in the config, e.g. ['V', 'A1'].
	:return (bool): a boolean indicating if tag is in srl_args. 
	"""
	flag = False
	if srl_args == 'all':
		if tag != 'O':
			flag = True
	else:
		tag = tag.split('-')
		for srl_arg in srl_args:
			if srl_arg in tag:
				flag = True
				break
	return flag

def load_trg_probe_lexicon(fr, level="fine"):
	"""Loads the trigger probe lexicon. 
	"""
	lexicon = {}
	if level == 'fine': # fine-grained event types (i.e. ACE event "subtypes"), e.g. "BE-BORN"
		for line in fr:
			line = line.strip()
			if line:
				if line.isupper():
					event_type = line
				else:
					lexicon[event_type] = line
	elif level == 'coarse': # coarse-grained event types (i.e. ACE event "types"), e.g. "LIFE"
		for line in fr:
			line = line.strip()
			if line:
				if line[:4] == 'type':
					event_type = line[5:]
				elif line[:8] == 'question':
					question = line[9:]
					lexicon[event_type] = {'question':question, 'subtypes':[]}
				else:
					subtype = line
					lexicon[event_type]['subtypes'].append(subtype)
	return lexicon

def load_arg_map(fr):
	"""Loads the mapping from SRL arg names to ACE arg names.  
	"""
	arg_map = {}
	for line in fr:
		line = line.strip()
		if line:
			if line.isupper():
				event_type = line
				arg_map[event_type] = {}
			else:
				srl_arg, ace_args = line.split(':')[0],line.split(':')[1]
				ace_args = [arg for arg in ace_args.split(',') if '+' not in arg]
				arg_map[event_type][srl_arg] = ace_args
	return arg_map

def load_arg_probe_lexicon(fr, arg_probe_type):
	"""Loads the argument probe lexicon.  
	"""
	probe_lexicon = {}
	for line in fr:
		line = line.strip()
		if line:
			if line.isupper():
				event_type = line
				probe_lexicon[event_type] = {}
			else:
				arg, probe = line.split(':')[0], line.split(':')[1]
				if arg_probe_type == 'auto_issth':
					probe = probe + ' is {}.'
				if arg_probe_type == 'auto_sthis':
					probe = '{} is ' + probe[0].lower() + probe[1:].lower() + '.'
				probe_lexicon[event_type][arg] = probe
	return probe_lexicon

def get_verb_srl(verb_srl_dict, instance):
	"""Get verbSRL output for an instance."""

	sent_id = instance.sent_id
	tokens_gold = instance.tokens
	srl_output = verb_srl_dict[sent_id]
	srl_output["words"] = [word for word in srl_output["words"] if word != "\\"]
	tokens_srl = srl_output['words']
	if tokens_srl != tokens_gold:
		srl2gold_id_map = get_gold_map(tokens_srl, tokens_gold)
	else:
		srl2gold_id_map = {i:i for i in range(len(tokens_srl))}
	return srl_output, srl2gold_id_map

def get_nom_srl(nom_srl_dict, instance):
	"""Gets nomSRL output for an instance."""
	
	sent_id = instance.sent_id
	tokens_gold = instance.tokens

	srl_output = nom_srl_dict[sent_id]
	srl_output["words"] = [word for word in srl_output["words"] if word != "\\"]
	tokens_srl = srl_output['words']
	if tokens_srl != tokens_gold:
		srl2gold_id_map = get_gold_map(tokens_srl, tokens_gold)
	else:
		srl2gold_id_map = {i:i for i in range(len(tokens_srl))}
	return srl_output, srl2gold_id_map

def load_srl(input_file):
	"""Loads cached SRL predictions for an input file."""
	
	verb_srl_dict, nom_srl_dict = {}, {}

	if "ACE" in input_file:
		dataset = "ACE"
	elif "ERE" in input_file:
		dataset = "ERE"
	else:
		raise ValueError("Unknown dataset")

	split = input_file.split('/')[-1].split('.')[0]

	for type in ['verb', 'nom']:
		path = None
		path = f"data/srl_output/{dataset}/{split}/{type}SRL_{srl_model}_{split}.jsonl"
		with open(path, 'r') as fr:
			for line in fr:
				srl_res = json.loads(line)
				sent_id = srl_res["sent_id"]
				if type == 'nom':
					nom_srl_dict[sent_id] = {"nominals": srl_res["nominals"],
										 "words": srl_res["words"],
										 }
				if type == 'verb':
					verb_srl_dict[sent_id] = {"verbs": srl_res["verbs"],
										 "words": srl_res["words"],
										 }
	return verb_srl_dict, nom_srl_dict

def get_head(dependency_parser, span, tokens, pos_tags):
	""" A coarse-grained head identifier. """
	
	instance = dependency_parser._dataset_reader.text_to_instance(tokens, pos_tags)
	output = dependency_parser.predict_instance(instance)

	start_ix = span[0]

	root_idx = output['predicted_heads'].index(0)
	pos_list = output['pos']
	words_list = output['words']
	parent_idx = 0
	current_idx = root_idx
	siblings = [current_idx]
	pos_in_siblings = 0
	while True:
		if pos_list[current_idx].startswith(('NN', 'PRP', 'CD')):
			word = words_list[current_idx]
			global_idx = start_ix + current_idx
			return global_idx, word
		pos_in_siblings = pos_in_siblings - 1
		if pos_in_siblings >= 0:  # check if there are siblings on the left of the current node
			current_idx = siblings[pos_in_siblings]  # if yes, move to the rightmost sibling
		else:  # if no, move to the rightmost child of the current node
			parent_idx = current_idx + 1
			siblings = [i for i, x in enumerate(output['predicted_heads']) if x == parent_idx]
			if siblings:
				current_idx = siblings[-1]
				pos_in_siblings = len(siblings) - 1
			else:
				return None, None

def find_lowest_constituent(predictor, trigger_text, sent):
	pred = predictor.predict(sentence=sent)
	root = pred['hierplane_tree']['root']
	cur_node = root
	
	parent_level = 0
	level_stack = [[root]]
	if_still_child = True

	while if_still_child:
		if_still_child = False
		for node in level_stack[-1]:
			if 'children' in node:
				if_still_child = True
				if len(level_stack) == parent_level + 1:
					level_stack.append([])
				for child in node['children']:
					level_stack[-1].append(child)
		parent_level += 1
	slim_level_stack = []
	for level in level_stack:
		slim_level_stack.append([])
		for node in level:
			slim_level_stack[-1].append({'word': node['word'],
										 'type': node['nodeType']})

	for level_id in range(len(slim_level_stack) - 1, -1, -1):
		level = slim_level_stack[level_id]
		for node in level:
			if (trigger_text in node['word'] or node['word'] in trigger_text) and \
							' ' in node['word'] and \
							node['type'] in ['NP','PP', 'S']:
				return node['word']



def generate_vocabs(datasets):
	"""Generates vocabularies from a list of data sets
	:param datasets (list): A list of data sets
	:return (dict): A dictionary of vocabs
	"""
	event_type_set = set()
	role_type_set = set()
	for dataset in datasets:
		event_type_set.update(dataset.event_type_set)
		role_type_set.update(dataset.role_type_set)

	# entity and trigger labels
	prefix = ['B', 'I']
	trigger_label_stoi = {'O': 0}

	for t in event_type_set:
		for p in prefix:
			trigger_label_stoi['{}-{}'.format(p, t)] = len(trigger_label_stoi)


	event_type_stoi = {k: i for i, k in enumerate(event_type_set, 1)}
	event_type_stoi['O'] = 0


	role_type_stoi = {k: i for i, k in enumerate(role_type_set, 1)}
	role_type_stoi['O'] = 0


	return {
		'event_type': event_type_stoi,
		'role_type': role_type_stoi,
		'trigger_label': trigger_label_stoi,
	}


def load_valid_patterns(path, vocabs):
	event_type_vocab = vocabs['event_type']
	entity_type_vocab = vocabs['entity_type']
	relation_type_vocab = vocabs['relation_type']
	role_type_vocab = vocabs['role_type']

	# valid event-role
	valid_event_role = set()
	event_role = json.load(
		open(os.path.join(path, 'event_role.json'), 'r', encoding='utf-8'))
	for event, roles in event_role.items():
		if event not in event_type_vocab:
			continue
		event_type_idx = event_type_vocab[event]
		for role in roles:
			if role not in role_type_vocab:
				continue
			role_type_idx = role_type_vocab[role]
			valid_event_role.add(event_type_idx * 100 + role_type_idx)

	# valid relation-entity
	valid_relation_entity = set()
	relation_entity = json.load(
		open(os.path.join(path, 'relation_entity.json'), 'r', encoding='utf-8'))
	for relation, entities in relation_entity.items():
		relation_type_idx = relation_type_vocab[relation]
		for entity in entities:
			entity_type_idx = entity_type_vocab[entity]
			valid_relation_entity.add(
				relation_type_idx * 100 + entity_type_idx)

	# valid role-entity
	valid_role_entity = set()
	role_entity = json.load(
		open(os.path.join(path, 'role_entity.json'), 'r', encoding='utf-8'))
	for role, entities in role_entity.items():
		if role not in role_type_vocab:
			continue
		role_type_idx = role_type_vocab[role]
		for entity in entities:
			entity_type_idx = entity_type_vocab[entity]
			valid_role_entity.add(role_type_idx * 100 + entity_type_idx)

	return {
		'event_role': valid_event_role,
		'relation_entity': valid_relation_entity,
		'role_entity': valid_role_entity
	}


def read_ltf(path):
	root = et.parse(path, et.XMLParser(
		dtd_validation=False, encoding='utf-8')).getroot()
	doc_id = root.find('DOC').get('id')
	doc_tokens = []
	for seg in root.find('DOC').find('TEXT').findall('SEG'):
		seg_id = seg.get('id')
		seg_tokens = []
		seg_start = int(seg.get('start_char'))
		seg_text = seg.find('ORIGINAL_TEXT').text
		for token in seg.findall('TOKEN'):
			token_text = token.text
			start_char = int(token.get('start_char'))
			end_char = int(token.get('end_char'))
			assert seg_text[start_char - seg_start:
							end_char - seg_start + 1
							] == token_text, 'token offset error'
			seg_tokens.append((token_text, start_char, end_char))
		doc_tokens.append((seg_id, seg_tokens))

	return doc_tokens, doc_id


def read_txt(path, language='english'):
	doc_id = os.path.basename(path)
	data = open(path, 'r', encoding='utf-8').read()
	data = [s.strip() for s in data.split('\n') if s.strip()]
	sents = [l for ls in [sent_tokenize(line, language=language) for line in data]
			 for l in ls]
	doc_tokens = []
	offset = 0
	for sent_idx, sent in enumerate(sents):
		sent_id = '{}-{}'.format(doc_id, sent_idx)
		tokens = word_tokenize(sent)
		tokens = [(token, offset + i, offset + i + 1)
				  for i, token in enumerate(tokens)]
		offset += len(tokens)
		doc_tokens.append((sent_id, tokens))
	return doc_tokens, doc_id


def read_json(path):
	with open(path, 'r', encoding='utf-8') as r:
		data = [json.loads(line) for line in r]
	doc_id = data[0]['doc_id']
	offset = 0
	doc_tokens = []

	for inst in data:
		tokens = inst['tokens']
		tokens = [(token, offset + i, offset + i + 1)
				  for i, token in enumerate(tokens)]
		offset += len(tokens)
		doc_tokens.append((inst['sent_id'], tokens))
	return doc_tokens, doc_id


def read_json_single(path):
	with open(path, 'r', encoding='utf-8') as r:
		data = [json.loads(line) for line in r]
	doc_id = os.path.basename(path)
	doc_tokens = []
	for inst in data:
		tokens = inst['tokens']
		tokens = [(token, i, i + 1) for i, token in enumerate(tokens)]
		doc_tokens.append((inst['sent_id'], tokens))
	return doc_tokens, doc_id


def save_result(output_file, gold_graphs, pred_graphs, sent_ids, tokens=None):
	with open(output_file, 'w', encoding='utf-8') as w:
		for i, (gold_graph, pred_graph, sent_id) in enumerate(
				zip(gold_graphs, pred_graphs, sent_ids)):
			output = {'sent_id': sent_id,
					  'gold': gold_graph.to_dict(),
					  'pred': pred_graph.to_dict()}
			if tokens:
				output['tokens'] = tokens[i]
			w.write(json.dumps(output) + '\n')


def mention_to_tab(start, end, entity_type, mention_type, mention_id, tokens, token_ids, score=1):
	tokens = tokens[start:end]
	token_ids = token_ids[start:end]
	span = '{}:{}-{}'.format(token_ids[0].split(':')[0],
							 token_ids[0].split(':')[1].split('-')[0],
							 token_ids[1].split(':')[1].split('-')[1])
	mention_text = tokens[0]
	previous_end = int(token_ids[0].split(':')[1].split('-')[1])
	for token, token_id in zip(tokens[1:], token_ids[1:]):
		start, end = token_id.split(':')[1].split('-')
		start, end = int(start), int(end)
		mention_text += ' ' * (start - previous_end) + token
		previous_end = end
	return '\t'.join([
		'json2tab',
		mention_id,
		mention_text,
		span,
		'NIL',
		entity_type,
		mention_type,
		str(score)
	])


def json_to_mention_results(input_dir, output_dir, file_name,
							bio_separator=' '):
	mention_type_list = ['nam', 'nom', 'pro', 'nam+nom+pro']
	file_type_list = ['bio', 'tab']
	writers = {}
	for mention_type in mention_type_list:
		for file_type in file_type_list:
			output_file = os.path.join(output_dir, '{}.{}.{}'.format(file_name,
																	 mention_type,
																	 file_type))
			writers['{}_{}'.format(mention_type, file_type)
					] = open(output_file, 'w')

	json_files = glob.glob(os.path.join(input_dir, '*.json'))
	for f in json_files:
		with open(f, 'r', encoding='utf-8') as r:
			for line in r:
				result = json.loads(line)
				doc_id = result['doc_id']
				tokens = result['tokens']
				token_ids = result['token_ids']
				bio_tokens = [[t, tid, 'O']
							  for t, tid in zip(tokens, token_ids)]
				# separate bio output
				for mention_type in ['NAM', 'NOM', 'PRO']:
					tokens_tmp = deepcopy(bio_tokens)
					for start, end, enttype, mentype in result['graph']['entities']:
						if mention_type == mentype:
							tokens_tmp[start] = 'B-{}'.format(enttype)
							for token_idx in range(start + 1, end):
								tokens_tmp[token_idx] = 'I-{}'.format(
									enttype)
					writer = writers['{}_bio'.format(mention_type.lower())]
					for token in tokens_tmp:
						writer.write(bio_separator.join(token) + '\n')
					writer.write('\n')
				# combined bio output
				tokens_tmp = deepcopy(bio_tokens)
				for start, end, enttype, _ in result['graph']['entities']:
					tokens_tmp[start] = 'B-{}'.format(enttype)
					for token_idx in range(start + 1, end):
						tokens_tmp[token_idx] = 'I-{}'.format(enttype)
				writer = writers['nam+nom+pro_bio']
				for token in tokens_tmp:
					writer.write(bio_separator.join(token) + '\n')
				writer.write('\n')
				# separate tab output
				for mention_type in ['NAM', 'NOM', 'PRO']:
					writer = writers['{}_tab'.format(mention_type.lower())]
					mention_count = 0
					for start, end, enttype, mentype in result['graph']['entities']:
						if mention_type == mentype:
							mention_id = '{}-{}'.format(doc_id, mention_count)
							tab_line = mention_to_tab(
								start, end, enttype, mentype, mention_id, tokens, token_ids)
							writer.write(tab_line + '\n')
				# combined tab output
				writer = writers['nam+nom+pro_tab']
				mention_count = 0
				for start, end, enttype, mentype in result['graph']['entities']:
					mention_id = '{}-{}'.format(doc_id, mention_count)
					tab_line = mention_to_tab(
						start, end, enttype, mentype, mention_id, tokens, token_ids)
					writer.write(tab_line + '\n')
	for w in writers:
		w.close()


def normalize_score(scores):
	min_score, max_score = min(scores), max(scores)
	if min_score == max_score:
		return [0] * len(scores)
	return [(s - min_score) / (max_score - min_score) for s in scores]


def best_score_by_task(log_file, task, max_epoch=1000):
	with open(log_file, 'r', encoding='utf-8') as r:
		config = r.readline()

		best_scores = []
		best_dev_score = 0
		for line in r:
			record = json.loads(line)
			dev = record['dev']
			test = record['test']
			epoch = record['epoch']
			if epoch > max_epoch:
				break
			if dev[task]['f'] > best_dev_score:
				best_dev_score = dev[task]['f']
				best_scores = [dev, test, epoch]

		print('Epoch: {}'.format(best_scores[-1]))
		tasks = ['entity', 'mention', 'relation', 'trigger_id', 'trigger',
				 'role_id', 'role']
		for t in tasks:
			print('{}: dev: {:.2f}, test: {:.2f}'.format(t,
														 best_scores[0][t][
															 'f'] * 100.0,
														 best_scores[1][t][
															 'f'] * 100.0))
