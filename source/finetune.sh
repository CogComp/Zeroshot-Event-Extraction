#!/usr/bin/env bash
## Finetune an extractive QA model on QAMR
# nohup python train_quase.py --target qamr --model mbert --cuda 0,1 > logs/finetune0.log 2>&1 &
# nohup python train_quase.py --target qamr --model xlm-roberta --cuda 2,3 > logs/finetune2.log 2>&1 &
# nohup python train_quase.py --mode train_eval --target qamr --model bert --cuda 2,5 > logs/bert_qamr.log 2>&1 &
# nohup python train_quase.py --mode train_eval --target qamr --model bert --cuda 2,3 > logs/bert_test.log 2>&1 &
# nohup python train_quase.py --mode train_eval --target qamr --model xlm --cuda 1 > logs/xlm.log 2>&1 &
# nohup python train_quase.py --mode train_eval --target qamr --model mbert-c --cuda 2 > logs/mbert-c.log 2>&1 &
# nohup python train_quase.py --mode train_eval --target qamr --model xlm-roberta-l --cuda 1 > logs/xlm-roberta-l.log 2>&1 &
# nohup python train_quase.py --mode train_eval --target qamr --model elior_bert-lc_mnli --cuda 5 > logs/elior_bert-lc_mnli_qamr.log 2>&1 &
# nohup python train_quase.py --mode train_eval --target qamr --model roberta-l --cuda 2 > logs/roberta-l_qamr.log 2>&1 &
# nohup python train_quase.py --mode train_eval --target qamr --model bert-l --cuda 3,4 > logs/bert-l_qamr.log 2>&1 &

### Finetune on QAMR-l_rep
#nohup python train_quase.py --mode train_eval --target qamr-l_rep --model bert --cuda 0 > logs/bert_qamr-l_rep.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target qamr-l_rep --model bert-l --cuda 1 > logs/bert-l_qamr-l_rep.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target qamr-l_rep --model roberta --cuda 2 > logs/roberta_qamr-l_rep.log 2>&1 &
##nohup python train_quase.py --mode train_eval --target qamr-l_rep --model roberta-l --cuda 3 > logs/roberta-l_qamr-l_rep.log 2>&1 &
### Finetune on QAMR-l_rand
#nohup python train_quase.py --mode train_eval --target qamr-l_rand --model bert --cuda 4 > logs/bert_qamr-l_rand.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target qamr-l_rand --model bert-l --cuda 5 > logs/bert-l_qamr-l_rand.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target qamr-l_rand --model roberta --cuda 6 > logs/roberta_qamr-l_rand.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target qamr-l_rand --model roberta-l --cuda 7 > logs/roberta-l_qamr-l_rand.log 2>&1 &


### Finetune on QAMR 1QA per sentence
#nohup python train_quase.py --mode train_eval --cuda 0 --target qamr_1qa_ctrl --model bert --mxlen 80 --train_bsize 12 --eval_bsize 8  > logs/bert_qamr_1qa_per_sent.log 2>&1 &
#nohup python train_quase.py --mode train_eval --cuda 1 --target qamr_1qa_ctrl --model bert-l --mxlen 80 --train_bsize 12 --eval_bsize 8  > logs/bert-l_qamr_1qa_per_sent.log 2>&1 &
#nohup python train_quase.py --mode train_eval --cuda 2 --target qamr_1qa_ctrl --model roberta --mxlen 80 --train_bsize 12 --eval_bsize 8  > logs/roberta_qamr_1qa_per_sent.log 2>&1 &
#nohup python train_quase.py --mode train_eval --cuda 3 --target qamr_1qa_per_sent --model roberta-l --mxlen 80 --train_bsize 12 --eval_bsize 8  > logs/roberta-l_qamr_1qa_per_sent.log 2>&1 &
### Finetune on QAMR 1QA ctrl set
#nohup python train_quase.py --mode train_eval --cuda 4 --target qamr_1qa_ctrl --model bert --mxlen 80 --train_bsize 12 --eval_bsize 8  > logs/bert_qamr_1qa_ctrl.log 2>&1 &
#nohup python train_quase.py --mode train_eval --cuda 5 --target qamr_1qa_ctrl --model bert-l --mxlen 80 --train_bsize 12 --eval_bsize 8  > logs/bert-l_qamr_1qa_ctrl.log 2>&1 &
#nohup python train_quase.py --mode train_eval --cuda 6 --target qamr_1qa_ctrl --model roberta --mxlen 80 --train_bsize 12 --eval_bsize 8  > logs/roberta_qamr_1qa_ctrl.log 2>&1 &
#nohup python train_quase.py --mode train_eval --cuda 7 --target qamr_1qa_ctrl --model roberta-l --mxlen 80 --train_bsize 12 --eval_bsize 8  > logs/roberta-l_qamr_1qa_ctrl.log 2>&1 &


## Finetune an extractive QA model on QAMR + SQuAD 2.0
#nohup python train_quase.py --mode train_eval --target qamr-squad2 --model bert --cuda 0 > logs/bert_qamr+squad2.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target qamr-squad2 --model roberta --cuda 1 > logs/roberta_qamr+squad2.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target qamr-squad2 --model bert-l --cuda 2 > logs/bert-l_qamr+squad2.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target qamr-squad2 --model roberta-l --cuda 3 > logs/roberta-l_qamr+squad2.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target qamr-squad2 --model elior_bert-lc_mnli --cuda 6 > logs/elior_bert-lc_mnli_qamr+squad2.log 2>&1 &

## Finetune a model on SQuAD 2.0 only
#nohup python train_quase.py --mode train_eval --target squad2 --model elior_bert-lc_mnli --cuda 4 > logs/elior_bert-lc_mnli_squad2.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target squad2 --model mbert --cuda 0,1,2,3 > logs/mbert_squad2.log 2>&1 &

# Finetune a model on SQuAD 2.0 with 1-sent context
#nohup python train_quase.py --mode train_eval --target squad2_1sent --model roberta --cuda 3 > logs/roberta_squad2_1sent.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target squad2_1sent --model bert --cuda 4 > logs/bert_squad2_1sent.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target squad2_1sent --model elior_bert-lc_mnli --cuda 0 > logs/elior_bert-lc_mnli_squad2_1sent.log 2>&1 &

## Finetune on has-answer only SQUAD 2.0
#### HA only
#nohup python train_quase.py --mode train_eval --target squad2_ha --model bert --cuda 0 > logs/bert_squad2_ha.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target squad2_ha --model roberta --cuda 1 > logs/roberta_squad2_ha.log 2>&1 &
#### HA+NA of the same size (control)
#nohup python train_quase.py --mode train_eval --target squad2-s_na+ha --model bert --cuda 2 > logs/bert_squad2-s_na+ha.log 2>&1 &
#nohup python train_quase.py --mode train_eval --target squad2-s_na+ha --model roberta --cuda 3 > logs/roberta_squad2-s_na+ha.log 2>&1 &

## Evalaute model on SQuAD 2.0
#nohup python train_quase.py --mode eval --target squad2 --model elior_bert-lc_mnli_squad2 --null_score_diff_threshold 0.7638531526255684 --cuda 0,1,2,3 > logs/elior_bert-lc_mnli_squad2_eval_wthresh.log 2>&1 &

## Finetune on MLQA
#nohup python train_quase.py --mode train_eval --target MLQA --train_file test-context-zh-question-en.json --pred_file dev-context-zh-question-en.json --model squad2_mbert --cuda 0,1 > logs/mbert_squad2_MLQAzhen.log 2>&1 &


## Evalaute model on ACE na-question
#nohup python train_quase.py --mode eval --target elior_ACE_na --pred_file ace_wh_has_answer.json --model elior_bert-lc_mnli_squad2 --cuda 0 &
#nohup python train_quase.py --mode eval --target elior_ACE_na --pred_file ace_wh_compet_idk.json --model elior_bert-lc_mnli_squad2 --cuda 0 &
#nohup python train_quase.py --mode eval --target elior_ACE_na --pred_file ace_wh_non_compet_idk.json --model elior_bert-lc_mnli_squad2 --cuda 0 &
#nohup python train_quase.py --mode eval --target elior_ACE_na --pred_file ace_wh_has_answer.json --model elior_bert-lc_mnli_squad2 --null_score_diff_threshold 0.7638531526255684 --cuda 0 &
#nohup python train_quase.py --mode eval --target elior_ACE_na --pred_file ace_wh_compet_idk.json --model elior_bert-lc_mnli_squad2 --null_score_diff_threshold 0.7638531526255684 --cuda 0 &
#nohup python train_quase.py --mode eval --target elior_ACE_na --pred_file ace_wh_non_compet_idk.json --model elior_bert-lc_mnli_squad2 --null_score_diff_threshold 0.7638531526255684 --cuda 0 &


## Finetune a Y/N model on BoolQ (without IDK)
# nohup python train_yn.py --mode train_eval --target MRPC --model bert --cuda 2 > logs/MPRC.log 2>&1 &
# nohup python train_yn.py --mode train_eval --task WNLI --target boolq --model bert --cuda 5 > logs/boolq_bert.log 2>&1 &
# nohup python train_yn.py --mode train_eval --task WNLI --target boolq --model roberta --cuda 3 > logs/boolq_roberta.log 2>&1 &
# nohup python train_yn.py --mode train_eval --task WNLI --target boolq --model bert-l --cuda 6 > logs/boolq_bertl.log 2>&1 &
# nohup python train_yn.py --mode train_eval --task WNLI --target boolq --model roberta-l --cuda 7 > logs/boolq_robertal.log 2>&1 &


## Finetune a Y/N QA model on BoolQ with IDK
# nohup python train_yn.py --mode train_eval --task RTE --target boolq_idk --model bert --cuda 0 > logs/boolq_idk_bert.log 2>&1 &
# nohup python train_yn.py --mode train_eval --task RTE --target boolq_idk --model bert-l --cuda 0 > logs/boolq_idk_bertl.log 2>&1 &
# nohup python train_yn.py --mode train_eval --task RTE --target boolq_idk --model roberta --cuda 6 > logs/boolq_idk_roberta.log 2>&1 &
# nohup python train_yn.py --mode train_eval --task RTE --target boolq_idk --model roberta-l --cuda 4 > logs/boolq_idk_robertal_test.log 2>&1 &


## Continue finetuning pretrained Y/N QA models (with IDK) on the annotation guideline
# nohup python train_yn.py --mode transfer --task RTE --target anno_gdl --source boolq_idk --model bert --cuda 0 > logs/anno_gdl_boolq_idk_bert.log 2>&1 &
# nohup python train_yn.py --mode transfer --task RTE --target anno_gdl --source boolq_idk --model bert-l --cuda 1 > logs/anno_gdl_boolq_idk_bert-l.log 2>&1 &
# nohup python train_yn.py --mode transfer --task RTE --target anno_gdl --source boolq_idk --model roberta --cuda 2 > logs/anno_gdl_boolq_idk_roberta.log 2>&1 &
# nohup python train_yn.py --mode transfer --task RTE --target anno_gdl --source boolq_idk --model roberta-l --cuda 4 > logs/anno_gdl_boolq_idk_roberta-l.log 2>&1 &


## Continue finetuning a pretrained TE model (roberta-large-mnli) on the annotation guidleine  
# nohup python train_te.py --mode train_eval --task WNLI --target gdl_te_pos_neg --model roberta-large-mnli --cuda 1 > logs/gdl_te_pos_neg_robertal.log 2>&1 &
# nohup python train_te.py --mode train_eval --task WNLI --target gdl_te_pos_only --model roberta-large-mnli --cuda 0 > logs/gdl_te_pos_only_robertal.log 2>&1 &

## Finetune vanilla model on MNLI
#nohup python train_te.py --mode train_eval --task MNLI --target MNLI_s --model roberta --cuda 0 > logs/mnlis_roberta_b.log 2>&1 &
#nohup python train_te.py --mode train_eval --task MNLI --target MNLI_s --model roberta-l --cuda 1 > logs/mnlis_roberta.log 2>&1 &
#nohup python train_te.py --mode train_eval --task MNLI --target MNLI_s --model bert --cuda 2 > logs/mnlis_bert.log 2>&1 &
#nohup python train_te.py --mode train_eval --task MNLI --target MNLI_s --model bert-l --cuda 3 > logs/mnlis_bertl.log 2>&1 &


#### Binary classifier for has-answer vs. no-answer questions ####
# Train the binary classifier on squad2.0
#nohup python train_te.py --mode train_eval --task WNLI --target squad2_cls --model bert --cuda 0 > logs/ha_na_cls_bert.log 2>&1 &
#nohup python train_te.py --mode train_eval --task WNLI --target squad2_cls --model bert-l --cuda 1 > logs/ha_na_cls_bert-l.log 2>&1 &
#nohup python train_te.py --mode train_eval --task WNLI --target squad2_cls --model roberta --cuda 2 > logs/ha_na_cls_roberta.log 2>&1 &
#nohup python train_te.py --mode train_eval --task WNLI --target squad2_cls --model roberta-l --cuda 5 > logs/ha_na_cls_roberta-l.log 2>&1 &

# Evaluate binary classifier on ACE
#nohup python train_te.py --mode eval --task WNLI --target ACE_ha_na_cls/ex_wtrg --model squad2_cls_bert --cuda 2 > logs/ha_na_cls_bert_aceeval.log 2>&1 &
#nohup python train_te.py --mode eval --task WNLI --target ACE_ha_na_cls/ex_wtrg --model squad2_cls_bert-l --cuda 2 > logs/ha_na_cls_bert-l_aceeval.log 2>&1 &
#nohup python train_te.py --mode eval --task WNLI --target ACE_ha_na_cls/ex_wtrg --model squad2_cls_roberta --cuda 4 > logs/ha_na_cls_roberta_aceeval.log 2>&1 &
#nohup python train_te.py --mode eval --task WNLI --target ACE_ha_na_cls/ex_wtrg --model squad2_cls_roberta-l --cuda 6 > logs/ha_na_cls_roberta-l_aceeval.log 2>&1 &

#nohup python train_te.py --mode eval --task WNLI --target ACE_ha_na_cls/ex --model squad2_cls_bert --cuda 7 > logs/ha_na_cls_bert_aceeval.log 2>&1 &
#nohup python train_te.py --mode eval --task WNLI --target ACE_ha_na_cls/ex --model squad2_cls_bert-l --cuda 2 > logs/ha_na_cls_bert-l_aceeval.log 2>&1 &
#nohup python train_te.py --mode eval --task WNLI --target ACE_ha_na_cls/ex --model squad2_cls_roberta --cuda 4 > logs/ha_na_cls_roberta_aceeval.log 2>&1 &
#nohup python train_te.py --mode eval --task WNLI --target ACE_ha_na_cls/ex --model squad2_cls_roberta-l --cuda 6 > logs/ha_na_cls_roberta-l_aceeval.log 2>&1 &
