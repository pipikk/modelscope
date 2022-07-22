import importlib
from typing import Dict, List, Optional, Union

import torch
import torch.nn.functional as F
from torch import nn

from ....metainfo import Heads
from ....outputs import OutputKeys
from ....utils.constant import Tasks
from ...base import TorchHead
from ...builder import HEADS


@HEADS.register_module(
    Tasks.text_classification, module_name=Heads.text_classification)
class SequenceClassificationHead(TorchHead):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        config = self.config
        self.num_labels = config.num_labels
        self.config = config
        classifier_dropout = (
            config['classifier_dropout'] if config.get('classifier_dropout')
            is not None else config['hidden_dropout_prob'])
        self.dropout = nn.Dropout(classifier_dropout)
        self.classifier = nn.Linear(config['hidden_size'],
                                    config['num_labels'])

    def forward(self, inputs=None):
        if isinstance(inputs, dict):
            assert inputs.get('pooled_output') is not None
            pooled_output = inputs.get('pooled_output')
        else:
            pooled_output = inputs
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return {OutputKeys.LOGITS: logits}

    def compute_loss(self, outputs: Dict[str, torch.Tensor],
                     labels) -> Dict[str, torch.Tensor]:
        logits = outputs[OutputKeys.LOGITS]
        return {OutputKeys.LOSS: F.cross_entropy(logits, labels)}