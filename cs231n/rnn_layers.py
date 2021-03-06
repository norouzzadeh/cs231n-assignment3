import numpy as np


"""
This file defines layer types that are commonly used for recurrent neural
networks.
"""


def rnn_step_forward(x, prev_h, Wx, Wh, b):
  """
  Run the forward pass for a single timestep of a vanilla RNN that uses a tanh
  activation function.

  The input data has dimension D, the hidden state has dimension H, and we use
  a minibatch size of N.

  Inputs:
  - x: Input data for this timestep, of shape (N, D).
  - prev_h: Hidden state from previous timestep, of shape (N, H)
  - Wx: Weight matrix for input-to-hidden connections, of shape (D, H)
  - Wh: Weight matrix for hidden-to-hidden connections, of shape (H, H)
  - b: Biases of shape (H,)

  Returns a tuple of:
  - next_h: Next hidden state, of shape (N, H)
  - cache: Tuple of values needed for the backward pass.
  """
  next_h, cache = None, None
  ##############################################################################
  # TODO: Implement a single forward step for the vanilla RNN. Store the next  #
  # hidden state and any values you need for the backward pass in the next_h   #
  # and cache variables respectively.                                          #
  ##############################################################################
  next_h = np.tanh(prev_h.dot(Wh) + x.dot(Wx) + b) # yield NxH matrix


  cache = (Wx, Wh, x, prev_h)
  pass
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return next_h, cache


def rnn_step_backward(dnext_h, cache):
  """
  Backward pass for a single timestep of a vanilla RNN.
  
  Inputs:
  - dnext_h: Gradient of loss with respect to next hidden state
  - cache: Cache object from the forward pass
  
  Returns a tuple of:
  - dx: Gradients of input data, of shape (N, D)
  - dprev_h: Gradients of previous hidden state, of shape (N, H)
  - dWx: Gradients of input-to-hidden weights, of shape (N, H)
  - dWh: Gradients of hidden-to-hidden weights, of shape (H, H)
  - db: Gradients of bias vector, of shape (H,)
  """
  dx, dprev_h, dWx, dWh, db = None, None, None, None, None
  ##############################################################################
  # TODO: Implement the backward pass for a single step of a vanilla RNN.      #
  #                                                                            #
  # HINT: For the tanh function, you can compute the local derivative in terms #
  # of the output value from tanh.                                             #
  ##############################################################################

  # next_h is exactly the output of tanh (see above)
  # TODO(aroetter): are all these used? next_h think not
  (Wx, Wh, x, prev_h) = cache

  # derivative of tanh(x) => 1 - (tanh(x)^2)
  tanh_deriv = 1.0 - next_h**2

  # what is passed in as dnext_h is really dLoss/dtanH
  # arg is the argument to the tanh, i.e. arg == h*Wh + x*Wx + b
  # via chain rule: dLoss/dArg = dLoss/dtanH * dtanH/dArg
  # we name this dArg is short for dLoss/dArg
  dArg = dnext_h * tanh_deriv

  # remember arg = h*Wh + x*Wx + b
  # so dArg/dh = Wh, dArg/dx = Wx, dArg/dB = 1
  
  # chain rule: dLoss/dx = dLoss/dArg * dArg/dx
  dx = dArg.dot(Wx.T)
  # chain rule: dLoss/dprev_h = dLoss/dArg * dArg/dprev_h
  dprev_h = dArg.dot(Wh.T)

  # similarly, via chain rule:
  dWx = x.T.dot(dArg)
  dWh = prev_h.T.dot(dArg)
  db = dArg.sum(axis=0)
  
  pass
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return dx, dprev_h, dWx, dWh, db


def rnn_forward(x, h0, Wx, Wh, b):
  """
  Run a vanilla RNN forward on an entire sequence of data. We assume an input
  sequence composed of T vectors, each of dimension D. The RNN uses a hidden
  size of H, and we work over a minibatch containing N sequences. After running
  the RNN forward, we return the hidden states for all timesteps.
  
  Inputs:
  - x: Input data for the entire timeseries, of shape (N, T, D).
  - h0: Initial hidden state, of shape (N, H)
  - Wx: Weight matrix for input-to-hidden connections, of shape (D, H)
  - Wh: Weight matrix for hidden-to-hidden connections, of shape (H, H)
  - b: Biases of shape (H,)
  
  Returns a tuple of:
  - h: Hidden states for the entire timeseries, of shape (N, T, H).
  - cache: Values needed in the backward pass
  """
  ##############################################################################
  # TODO: Implement forward pass for a vanilla RNN running on a sequence of    #
  # input data. You should use the rnn_step_forward function that you defined  #
  # above.                                                                     #
  ##############################################################################
  h, cache = None, []
  N, T, D = x.shape
  H = h0.shape[1]
  
  next_h = h0
  h = np.empty((N, T, H))
  for t in xrange(T):
    curx = x[:,t,:] # has shape NxD
    (next_h, cur_cache) = rnn_step_forward(curx, next_h, Wx, Wh, b)
    h[:, t, :] = next_h # next_h is NxH
    cache.append(cur_cache)
  pass
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return h, cache


def rnn_backward(dh, cache):
  """
  Compute the backward pass for a vanilla RNN over an entire sequence of data.
  
  Inputs:
  - dh: Upstream gradients of all hidden states, of shape (N, T, H)
  
  Returns a tuple of:
  - dx: Gradient of inputs, of shape (N, T, D)
  - dh0: Gradient of initial hidden state, of shape (N, H)
  - dWx: Gradient of input-to-hidden weights, of shape (D, H)
  - dWh: Gradient of hidden-to-hidden weights, of shape (H, H)
  - db: Gradient of biases, of shape (H,)
  """
  dx, dh0, dWx, dWh, db = None, None, None, None, None
  ##############################################################################
  # TODO: Implement the backward pass for a vanilla RNN running an entire      #
  # sequence of data. You should use the rnn_step_backward function that you   #
  # defined above.                                                             #
  ##############################################################################
  N, T, H = dh.shape
  D = cache[0][1].shape[0]

  dx = np.empty((N, T, D))
  dprev_h = np.zeros((N, H))
  dWx = np.zeros((D, H))
  dWh = np.zeros((H, H))
  db = np.zeros(H)
  
  for t in reversed(xrange(T)):
    cur_cache = cache[t]
    # at each step, the derivative is the derivative i get from later
    # on in the computation (dh), as well as the derivative i got from
    # rnn_step_backward (dprev_h), which corresponds to the derivative
    # from future time steps
    total_dh = dh[:, t, :] + dprev_h
    (cur_dx, dprev_h, cur_dWx, cur_dWh, cur_db) = rnn_step_backward(
      total_dh, cur_cache)
    dx[:, t, :] = cur_dx
    dWx += cur_dWx
    dWh += cur_dWh
    db += cur_db
  # final hidden layer
  dh0 = dprev_h
  pass
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return dx, dh0, dWx, dWh, db


def word_embedding_forward(x, W):
  """
  Forward pass for word embeddings. We operate on minibatches of size N where
  each sequence has length T. We assume a vocabulary of V words, assigning each
  to a vector of dimension D.
  
  Inputs:
  - x: Integer array of shape (N, T) giving indices of words. Each element idx
    of x muxt be in the range 0 <= idx < V.
  - W: Weight matrix of shape (V, D) giving word vectors for all words.
  
  Returns a tuple of:
  - out: Array of shape (N, T, D) giving word vectors for all input words.
  - cache: Values needed for the backward pass
  """
  out, cache = None, None
  ##############################################################################
  # TODO: Implement the forward pass for word embeddings.                      #
  #                                                                            #
  # HINT: This should be very simple.                                          #
  ##############################################################################

  # I'll i'm doing is a lookup. each string out of the N i have is made of
  # T words. All I do is lookup that word (an index 0 <= idx < V) and swap
  # it for the corresponding D delement vector.

  N, T = x.shape
  D = W.shape[1]

  out = np.empty((N, T, D))
  for n in xrange(N):
    cur_seq = x[n]
    out[n, :, :] = W[cur_seq]
  # TODO(aroetter: save the cache
  V = W.shape[0]
  cache = (x, V)
  pass
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return out, cache


def word_embedding_backward(dout, cache):
  """
  Backward pass for word embeddings. We cannot back-propagate into the words
  since they are integers, so we only return gradient for the word embedding
  matrix.
  
  HINT: Look up the function np.add.at
  
  Inputs:
  - dout: Upstream gradients of shape (N, T, D)
  - cache: Values from the forward pass
  
  Returns:
  - dW: Gradient of word embedding matrix, of shape (V, D).
  """
  dW = None
  ##############################################################################
  # TODO: Implement the backward pass for word embeddings.                     #
  #                                                                            #
  # HINT: Look up the function np.add.at                                       #
  ##############################################################################
  x, V = cache
  N, T, D = dout.shape

  dW = np.zeros((V, D))
  for n in range(N):
    indexes = x[n, :] # of shape T...there are T words in this datapt
    gradients = dout[n, :, :] # of shape TxD.
    # logically what this is doing is:
    # loop over every word in the current datapt. (stored in indexes)
    #   lookup the D gradients for that word
    #   add those D gradients to the relevant row (for the cur word) in dW
    # indexes is used to both slice into gradients (for reading), and into dW
    #   (for incrementing)
    np.add.at(dW, indexes, gradients)
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return dW


def sigmoid(x):
  """
  A numerically stable version of the logistic sigmoid function.
  """
  pos_mask = (x >= 0)
  neg_mask = (x < 0)
  z = np.zeros_like(x)
  z[pos_mask] = np.exp(-x[pos_mask])
  z[neg_mask] = np.exp(x[neg_mask])
  top = np.ones_like(x)
  top[neg_mask] = z[neg_mask]
  return top / (1 + z)


def lstm_step_forward(x, prev_h, prev_c, Wx, Wh, b):
  """
  Forward pass for a single timestep of an LSTM.
  
  The input data has dimension D, the hidden state has dimension H, and we use
  a minibatch size of N.
  
  Inputs:
  - x: Input data, of shape (N, D)
  - prev_h: Previous hidden state, of shape (N, H)
  - prev_c: previous cell state, of shape (N, H)
  - Wx: Input-to-hidden weights, of shape (D, 4H)
  - Wh: Hidden-to-hidden weights, of shape (H, 4H)
  - b: Biases, of shape (4H,)
  
  Returns a tuple of:
  - next_h: Next hidden state, of shape (N, H)
  - next_c: Next cell state, of shape (N, H)
  - cache: Tuple of values needed for backward pass.
  """
  next_h, next_c, cache = None, None, None
  #############################################################################
  # TODO: Implement the forward pass for a single timestep of an LSTM.        #
  # You may want to use the numerically stable sigmoid implementation above.  #
  #############################################################################
  H = prev_h.shape[1]
  a = x.dot(Wx) + prev_h.dot(Wh) + b # a is of shape Nx4H

  # each is NxH
  (a_i, a_f, a_o, a_g) = np.split(a, 4, axis=1)
  i, f, o  = sigmoid(a_i), sigmoid(a_f), sigmoid(a_o)
  g = np.tanh(a_g)

  next_c = f * prev_c + i * g
  next_h = o * np.tanh(next_c)
  
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################

  cache = (i, f, o, g, next_c, prev_c, prev_h, Wx, Wh, x)
  
  return next_h, next_c, cache


def lstm_step_backward(dnext_h, dnext_c, cache):
  """
  Backward pass for a single timestep of an LSTM.
  
  Inputs:
  - dnext_h: Gradients of next hidden state, of shape (N, H)
  - dnext_c: Gradients of next cell state, of shape (N, H)
  - cache: Values from the forward pass
  
  Returns a tuple of:
  - dx: Gradient of input data, of shape (N, D)
  - dprev_h: Gradient of previous hidden state, of shape (N, H)
  - dprev_c: Gradient of previous cell state, of shape (N, H)
  - dWx: Gradient of input-to-hidden weights, of shape (D, 4H)
  - dWh: Gradient of hidden-to-hidden weights, of shape (H, 4H)
  - db: Gradient of biases, of shape (4H,)
  """
  dx, dWx, dWh, db = None, None, None, None
  #############################################################################
  # TODO: Implement the backward pass for a single timestep of an LSTM.       #
  #                                                                           #
  # HINT: For sigmoid and tanh you can compute local derivatives in terms of  #
  # the output value from the nonlinearity.                                   #
  #############################################################################
  (i, f, o, g, next_c, prev_c, prev_h, Wx, Wh, x) = cache

  tanh_next_c = np.tanh(next_c)

  # one thing we'll need over and over is the derivative of loss wrt
  # dnext_c, VIA the next_h equation.
  # dLoss/dnext_c = dloss/dnext_h * dnext_h/dnext_c
  alt_dnext_c = dnext_h * o * (1-np.power(tanh_next_c, 2))
  
  # many of this gradients contribute in 2 ways, once via next_c, once
  # via next_h. here we call those paths 1 and 2, just for clarity.

  # Path 1 (via next_c). dloss/dprev_c = dloss/dnext_c * dnext_c/dprev_c
  dprev_c = dnext_c * f
  # Path 2 (via next_h). dloss/dprev_c = alt_dnext_c * dnext_c/d_prevc
  dprev_c += alt_dnext_c * f

  # compute do. only contributes via path 2, via next_h
  # Path 2 (via H): dLoss/do = dLoss/dnext_h * dnext_h / do
  do = dnext_h * tanh_next_c

  # compute df
  # Path 1 (via next_c): dLoss/df = dLoss/dnext_c * dnext_c/df
  df = dnext_c * prev_c
  # Path 2 (via next_h): dLoss/dh = alt_dnext_c * dnext_c/df
  df += alt_dnext_c * prev_c
  
  # compute di
  # Path 1 (via next_c): dLoss/di = dLoss/dnext_c * dnext_c/di
  di = dnext_c * g
  # Path 2 (via next_h): dLoss/di = alt_dnext_c * dnext_c/di
  di += alt_dnext_c * g

  # compute dg
  # Path 1 (via_next_c): dLoss/dg = dLoss/dnext_c * dnext_c/dg
  # Path 2 (via next_h): dLoss/dg = alt_dnext_c * dnext_c/dg
  dg = dnext_c * i
  dg += alt_dnext_c * i

  # now backprop through the sigmoids and tanh to get the a_*'s
  # dLoss/da_i = dLoss/di * di/da_i (remember sigmoid(a_i) == i)
  da_i = di * i * (1-i)
  da_f = df * f * (1-f)
  da_o = do * o * (1-o)
  # dLoss/da_g = dLoss/dg * dg/da_g (remember g = tanh(a_g))
  da_g = dg * (1-np.power(g, 2))

  # remember a is just the concatenation of a_i, a_f, a_o, a_g
  da = np.hstack((da_i, da_f, da_o, da_g))

  # Now using da we can compute a bunch of results
  # dLoss/dx = dLoss/da * da/dx
  dx = da.dot(Wx.T)

  # dLoss/dprev_h = dLoss/da * da/dprev_h
  dprev_h = da.dot(Wh.T)

  # dLoss/dWx = dLoss/da * da/dWx
  dWx = x.T.dot(da)
  
  # dLoss/dWh = dLoss/da * da/dWh
  dWh = prev_h.T.dot(da)

  # dLoss/db = dLoss/da * da/db
  db = da.sum(axis=0) 
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################

  return dx, dprev_h, dprev_c, dWx, dWh, db


def lstm_forward(x, h0, Wx, Wh, b):
  """
  Forward pass for an LSTM over an entire sequence of data. We assume an input
  sequence composed of T vectors, each of dimension D. The LSTM uses a hidden
  size of H, and we work over a minibatch containing N sequences. After running
  the LSTM forward, we return the hidden states for all timesteps.
  
  Note that the initial cell state is passed as input, but the initial cell
  state is set to zero. Also note that the cell state is not returned; it is
  an internal variable to the LSTM and is not accessed from outside.
  
  Inputs:
  - x: Input data of shape (N, T, D)
  - h0: Initial hidden state of shape (N, H)
  - Wx: Weights for input-to-hidden connections, of shape (D, 4H)
  - Wh: Weights for hidden-to-hidden connections, of shape (H, 4H)
  - b: Biases of shape (4H,)
  
  Returns a tuple of:
  - h: Hidden states for all timesteps of all sequences, of shape (N, T, H)
  - cache: Values needed for the backward pass.
  """
  #############################################################################
  # TODO: Implement the forward pass for an LSTM over an entire timeseries.   #
  # You should use the lstm_step_forward function that you just defined.      #
  #############################################################################
  N, T, D = x.shape
  H = h0.shape[1]
  h = np.empty((N, T, H))
  cache = []
  
  next_c = np.zeros((N, H))
  next_h = h0
  for t in xrange(T):
    curx = x[:,t,:] # has shape NxD
    (next_h, next_c, cur_cache) = lstm_step_forward(
      curx, next_h, next_c, Wx, Wh, b)
    h[:, t, :] = next_h
    cache.append(cur_cache)
  pass
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################

  return h, cache


def lstm_backward(dh, cache):
  """
  Backward pass for an LSTM over an entire sequence of data.]
  
  Inputs:
  - dh: Upstream gradients of hidden states, of shape (N, T, H)
  - cache: Values from the forward pass
  
  Returns a tuple of:
  - dx: Gradient of input data of shape (N, T, D)
  - dh0: Gradient of initial hidden state of shape (N, H)
  - dWx: Gradient of input-to-hidden weight matrix of shape (D, 4H)
  - dWh: Gradient of hidden-to-hidden weight matrix of shape (H, 4H)
  - db: Gradient of biases, of shape (4H,)
  """
  dx, dh0, dWx, dWh, db = None, None, None, None, None
  #############################################################################
  # TODO: Implement the backward pass for an LSTM over an entire timeseries.  #
  # You should use the lstm_step_backward function that you just defined.     #
  #############################################################################
  N, T, H = dh.shape
  D = cache[0][9].shape[1] #get an 'x' array from the cache. 2nd dim is D

  dx = np.empty((N, T, D))
  dprev_h = np.zeros((N, H))
  dprev_c = np.zeros((N, H))
  dWx = np.zeros((D, 4*H))
  dWh = np.zeros((H, 4*H))
  db = np.zeros(4*H)

  for t in reversed(xrange(T)):
    cur_cache = cache[t]
    total_dh = dh[:, t, :] + dprev_h
    (cur_dx, dprev_h, dprev_c, cur_dWx, cur_dWh, cur_db) = lstm_step_backward(
      total_dh, dprev_c, cur_cache)
    dx[:, t, :] = cur_dx
    dWx += cur_dWx
    dWh += cur_dWh
    db += cur_db
  # final hidden layer
  dh0 = dprev_h
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  
  return dx, dh0, dWx, dWh, db


def temporal_affine_forward(x, w, b):
  """
  Forward pass for a temporal affine layer. The input is a set of D-dimensional
  vectors arranged into a minibatch of N timeseries, each of length T. We use
  an affine function to transform each of those vectors into a new vector of
  dimension M.

  Inputs:
  - x: Input data of shape (N, T, D)
  - w: Weights of shape (D, M)
  - b: Biases of shape (M,)
  
  Returns a tuple of:
  - out: Output data of shape (N, T, M)
  - cache: Values needed for the backward pass
  """
  N, T, D = x.shape
  M = b.shape[0]
  out = x.reshape(N * T, D).dot(w).reshape(N, T, M) + b
  cache = x, w, b, out
  return out, cache


def temporal_affine_backward(dout, cache):
  """
  Backward pass for temporal affine layer.

  Input:
  - dout: Upstream gradients of shape (N, T, M)
  - cache: Values from forward pass

  Returns a tuple of:
  - dx: Gradient of input, of shape (N, T, D)
  - dw: Gradient of weights, of shape (D, M)
  - db: Gradient of biases, of shape (M,)
  """
  x, w, b, out = cache
  N, T, D = x.shape
  M = b.shape[0]

  dx = dout.reshape(N * T, M).dot(w.T).reshape(N, T, D)
  dw = dout.reshape(N * T, M).T.dot(x.reshape(N * T, D)).T
  db = dout.sum(axis=(0, 1))

  return dx, dw, db


def temporal_softmax_loss(x, y, mask, verbose=False):
  """
  A temporal version of softmax loss for use in RNNs. We assume that we are
  making predictions over a vocabulary of size V for each timestep of a
  timeseries of length T, over a minibatch of size N. The input x gives scores
  for all vocabulary elements at all timesteps, and y gives the indices of the
  ground-truth element at each timestep. We use a cross-entropy loss at each
  timestep, summing the loss over all timesteps and averaging across the
  minibatch.

  As an additional complication, we may want to ignore the model output at some
  timesteps, since sequences of different length may have been combined into a
  minibatch and padded with NULL tokens. The optional mask argument tells us
  which elements should contribute to the loss.

  Inputs:
  - x: Input scores, of shape (N, T, V)
  - y: Ground-truth indices, of shape (N, T) where each element is in the range
       0 <= y[i, t] < V
  - mask: Boolean array of shape (N, T) where mask[i, t] tells whether or not
    the scores at x[i, t] should contribute to the loss.

  Returns a tuple of:
  - loss: Scalar giving loss
  - dx: Gradient of loss with respect to scores x.
  """

  N, T, V = x.shape
  
  x_flat = x.reshape(N * T, V)
  y_flat = y.reshape(N * T)
  mask_flat = mask.reshape(N * T)
  
  probs = np.exp(x_flat - np.max(x_flat, axis=1, keepdims=True))
  probs /= np.sum(probs, axis=1, keepdims=True)
  loss = -np.sum(mask_flat * np.log(probs[np.arange(N * T), y_flat])) / N
  dx_flat = probs.copy()
  dx_flat[np.arange(N * T), y_flat] -= 1
  dx_flat /= N
  dx_flat *= mask_flat[:, None]
  
  if verbose: print 'dx_flat: ', dx_flat.shape
  
  dx = dx_flat.reshape(N, T, V)
  
  return loss, dx

