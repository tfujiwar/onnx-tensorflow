from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from collections import namedtuple

from onnx import TensorProto
import tensorflow as tf

# Using the following two functions to prevent shooting ourselves
# in the foot with non-invertible maps.

def invertible(dict):
    # invertible iff one-to-one and onto
    # onto is guaranteed, so check one-to-one
    return len(dict.values()) == len(set(dict.values()))

def invert(dict):
    if not invertible(dict):
        raise ValueError("The dictionary is not invertible"
            " because it is not one-to-one.")
    else:
        inverse = {v: k for k, v in dict.items()}
        return inverse

ONNX_TYPE_TO_TF_TYPE = {
    TensorProto.FLOAT: tf.float32,
    TensorProto.UINT8: tf.uint8,
    TensorProto.INT8: tf.int8,
    TensorProto.UINT16: tf.uint16,
    TensorProto.INT16: tf.int16,
    TensorProto.INT32: tf.int32,
    TensorProto.INT64: tf.int64,
    TensorProto.BOOL: tf.bool,
    TensorProto.FLOAT16: tf.float16,
    TensorProto.DOUBLE: tf.float64,
    TensorProto.COMPLEX64: tf.complex64,
    TensorProto.COMPLEX128: tf.complex128,
    # TODO: uncomment this in the future
    # TensorProto.UINT32: tf.uint32,
    # TensorProto.UINT64: tf.uint64,
}

STR_TO_TF_TYPE = {
  "float": tf.float32,
  "uint8": tf.uint8,
  "int8": tf.int8,
  "uint16": tf.uint16,
  "int16": tf.int16,
  "int32": tf.int32,
  "int64": tf.int64,
  "bool": tf.bool,
  "float16": tf.float16,
  "double": tf.float64,
  "complex64": tf.complex64,
  "complex128": tf.complex128,
  # TODO: uncomment this in the future
  # "uint32": tf.uint32,
  # "uint64": tf.uint64,
}

TF_TYPE_ENUM = [
  "undefined",
  tf.float32,
  tf.uint8,
  tf.int8,
  tf.uint16,
  tf.int16,
  tf.int32,
  tf.int64,
  tf.string,
  tf.bool,
  tf.float16,
  tf.float64,
  tf.complex64,
  tf.complex128,
  # TODO: uncomment this in the future
  # tf.uint32,
  # tf.uint64,
]

TF_TYPE_TO_ONNX_TYPE = invert(ONNX_TYPE_TO_TF_TYPE)

ONNX_ATTR_TO_TF_ATTR = {
  "scale": "stddev",
  "high": "maxval",
  "low": "minval",
  "axes": "axis",
  "keepdims": "keep_dims",
}

TF_ATTR_TO_ONNX_ATTR = invert(ONNX_ATTR_TO_TF_ATTR)

ONNX_ATTR_TO_TF_ATTR_PER_OP = {
  "cast": {
    "to": "dtype"
  },
  "gather": {
    "dim": "axis"
  },
}

TF_ATTR_TO_ONNX_ATTR_PER_OP = {k: invert(v) for k, v in ONNX_ATTR_TO_TF_ATTR_PER_OP.items()}

ONNX_ATTR_TO_REMOVE_PER_OP = {}

TF_ATTR_TO_REMOVE = ["_output_shapes", "T", "seed2", "Tidx"]

ONNX_OP_TO_TF_OP = {
  "abs": tf.abs,
  "cast": tf.cast,
  "ceil": tf.ceil,
  "concat": tf.concat,
  "dot": tf.contrib.keras.backend.dot,
  "exp": tf.exp,
  "floor": tf.floor,
  "gather": tf.gather,
  "hard_sigmoid": tf.keras.backend.hard_sigmoid,
  "hardmax": tf.contrib.seq2seq.hardmax,
  "log": tf.log,
  "log_softmax": tf.nn.log_softmax,
  "neg": tf.negative,
  "not": tf.logical_not,
  "pow": tf.pow,
  "random_normal": tf.random_normal,
  "random_uniform": tf.random_uniform,
  "reciprocal": tf.reciprocal,
  "reduce_log_sum_exp": tf.reduce_logsumexp,
  "reduce_max": tf.reduce_max,
  "reduce_mean": tf.reduce_mean,
  "reduce_min": tf.reduce_min,
  "reduce_prod": tf.reduce_prod,
  "reduce_sum": tf.reduce_sum,
  "relu": tf.nn.relu,
  "sigmoid": tf.sigmoid,
  "selu": tf.nn.selu,
  "shape": tf.shape,
  "size": tf.size,
  "softplus": tf.nn.softplus,
  "softsign": tf.nn.softsign,
  "sqrt": tf.sqrt,
  "squeeze": tf.squeeze,
  "tanh": tf.tanh,
  "thresholded_relu": tf.keras.layers.ThresholdedReLU,
  "top_k": tf.nn.top_k,
  "transpose": tf.transpose,
  "unsqueeze": tf.expand_dims,
}

TF_OP_TO_ONNX_OP = invert(ONNX_OP_TO_TF_OP)

TF_OP_STR_TO_ONNX_OP = {
  "LogicalNot": "Not",
  "Relu": "Relu",
  "Pow": "Pow",
  # TODO:
  # handle Mul, Add, Sub,
  # these are temporarily added to
  # test other ops
  "Mul": "Mul",
  "Add": "Add",

  "Reciprocal": "Reciprocal",
  "Sigmoid": "Sigmoid",
  "Sqrt": "Sqrt",
  "Tanh": "Tanh",
}

def get_tf_shape_as_list(tf_shape_dim):
  return list(map(lambda x: x.size, list(tf_shape_dim)))

# This function inserts an underscore before every upper
# case letter and lowers that upper case letter except for
# the first letter.
def op_name_to_lower(name):
  return re.sub('(?<!^)(?=[A-Z])', '_', name).lower()
