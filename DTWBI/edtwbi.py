import numpy as np
import pandas as po
from math import isinf 
from tqdm import tqdm
import matplotlib.pyplot as plt
from numpy import array, zeros, full, argmin, inf, ndim


def _traceback(D):
    i, j = array(D.shape) - 2
    p, q = [i], [j]
    while (i > 0) or (j > 0):
        tb = argmin((D[i, j], D[i, j + 1], D[i + 1, j]))
        if tb == 0:
            i -= 1
            j -= 1
        elif tb == 1:
            i -= 1
        else:  # (tb == 2):
            j -= 1
        p.insert(0, i)
        q.insert(0, j)
    return array(p), array(q)


def dtw(x, y, dist, warp=1, w=inf, s=1.0):
    """
    Computes Dynamic Time Warping (DTW) of two sequences.
    :param array x: N1*M array
    :param array y: N2*M array
    :param func dist: distance used as cost measure
    :param int warp: how many shifts are computed.
    :param int w: window size limiting the maximal distance between indices of matched entries |i,j|.
    :param float s: weight applied on off-diagonal moves of the path. As s gets larger, the warping path is increasingly biased towards the diagonal
    Returns the minimum distance, the cost matrix, the accumulated cost matrix, and the wrap path.
    """
    assert len(x)
    assert len(y)
    assert isinf(w) or (w >= abs(len(x) - len(y)))
    assert s > 0
    r, c = len(x), len(y)
    if not isinf(w):
        D0 = full((r + 1, c + 1), inf)
        for i in range(1, r + 1):
            D0[i, max(1, i - w):min(c + 1, i + w + 1)] = 0
        D0[0, 0] = 0
    else:
        D0 = zeros((r + 1, c + 1))
        D0[0, 1:] = inf
        D0[1:, 0] = inf
    D1 = D0[1:, 1:]  # view
    for i in range(r):
        for j in range(c):
            if (isinf(w) or (max(0, i - w) <= j <= min(c, i + w))):
                D1[i, j] = dist(i, j, x, y)
    C = D1.copy()
    jrange = range(c)
    for i in range(r):
        if not isinf(w):
            jrange = range(max(0, i - w), min(c, i + w + 1))
        for j in jrange:
            min_list = [D0[i, j]]
            for k in range(1, warp + 1):
                i_k = min(i + k, r)
                j_k = min(j + k, c)
                min_list += [D0[i_k, j] * s, D0[i, j_k] * s]
            D1[i, j] += min(min_list)
    if len(x) == 1:
        path = zeros(len(y)), range(len(y))
    elif len(y) == 1:
        path = range(len(x)), zeros(len(x))
    else:
        path = _traceback(D0)
    return D1[-1, -1], C, D1, path


def derivative_dtw_distance(i, j, x, y):
    if i+1 == len(x) or j+1 == len(y):
        dist = (x[i] - y[j])**2
    
    else:
        d_x_i = ((x[i] - x[i-1]) + (x[i+1] - x[i-1])/2)/2
        d_y_j = ((y[j] - y[j-1]) + (y[j+1] - y[j-1])/2)/2    

        dist = (d_x_i - d_y_j)**2

    return dist


x = np.random.randn(8, 1)
y = np.random.randn(11, 1)

d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=derivative_dtw_distance)

d

plt.imshow(acc_cost_matrix.T, origin='lower', cmap='gray', interpolation='nearest')
plt.plot(path[0], path[1], 'w')
plt.show()

df_17 = po.read_csv('../data/processed/2017_cleaned_for_imputation.csv')

plt.figure(figsize=(20,10))
plt.plot(df_17['W'][:288*10])

df_17.iloc[93]

x = df_17['W'].values.copy()

plt.figure(figsize=(20,10))
plt.plot(x[:288*10])

step = 5

missing_indices = []
for j in tqdm(range(93, 1000)):
    if np.isnan(x[j]):
        missing_indices.append(j)
        
    if len(missing_indices)!=0 and not np.isnan(x[j]):
        Da = x[missing_indices[-1]+1:]
        Db = x[:missing_indices[0]]
        Qa = Da[:len(missing_indices)]
        Qb = Db[-len(missing_indices):]
        
        dtw_costs_b = []
        next_win = ''
        min_cost_b = np.inf
        most_similar_win_b = ''
        for i in range(len(missing_indices), len(Db)-len(missing_indices),  step):
            ref_win = Db[i - len(missing_indices):i]
            if np.sum(ref_win == Qb) > 0:
                print(ref_win)
                raise ValueError
            d, cost_matrix, acc_cost_matrix, path = dtw(Qb, ref_win, dist=derivative_dtw_distance)
            dtw_costs_b.append(d)
            if d<min_cost_b:
                min_cost_b = d
                most_similar_win_b = ref_win
                next_win = Db[i + len(missing_indices) - len(missing_indices):i + len(missing_indices)]
                #print('New minima found')
        
        dtw_costs_a = []
        min_cost_a = np.inf
        prev_win = ''
        most_similar_win_a = ''
        for i in range(len(missing_indices), len(Da)-len(missing_indices),  step):
            ref_win = Da[i: i + len(missing_indices)]
            if np.sum(ref_win == Qa) > 0:
                print(ref_win)
                print(Qa)
                raise ValueError
            d, cost_matrix, acc_cost_matrix, path = dtw(Qa, ref_win, dist=derivative_dtw_distance)
            dtw_costs_a.append(d)
            if d<min_cost_a:
                min_cost_a = d
                most_similar_win_a = ref_win
                prev_win = Da[i - len(missing_indices): i + len(missing_indices) - len(missing_indices)]
                #print('New minima found')
        
        x[missing_indices] = (prev_win+next_win)/2
        
        missing_indices = []

plt.figure(figsize=(20,10))
plt.plot(df_17['W'][:288*5])

plt.figure(figsize=(20,10))
plt.plot(x[:288*10])





















len(missing_indices)

Da = x[missing_indices[-1]+1:]
Db = x[:missing_indices[0]]

Qa = Da[:len(missing_indices)]
Qb = Db[-len(missing_indices):]

len(Db[-len(missing_indices):])

len(Db)

200000000000000<np.inf

step = 1

dtw_costs_b = []
next_win = ''
min_cost_b = np.inf
most_similar_win_b = ''
for i in range(len(missing_indices), len(Db)-len(missing_indices),  step):
    ref_win = Db[i - len(missing_indices):i]
    if np.sum(ref_win == Qb) > 0:
        print(ref_win)
        raise ValueError
    d, cost_matrix, acc_cost_matrix, path = dtw(Qb, ref_win, dist=derivative_dtw_distance)
    dtw_costs_b.append(d)
    if d<min_cost_b:
        min_cost_b = d
        most_similar_win_b = ref_win
        next_win = Db[i + len(missing_indices) - len(missing_indices):i + len(missing_indices)]
        print('New minima found')

plt.plot(Qb, color='blue')
plt.plot(most_similar_win_b, color='red')
plt.plot(next_win, color='yellow')

next_win

dtw_costs_a = []
min_cost_a = np.inf
prev_win = ''
most_similar_win_a = ''
for i in tqdm(range(len(missing_indices), len(Da)-len(missing_indices),  step)):
    ref_win = Da[i: i + len(missing_indices)]
    if np.sum(ref_win == Qa) > 0:
        print(ref_win)
        print(Qa)
        raise ValueError
    d, cost_matrix, acc_cost_matrix, path = dtw(Qa, ref_win, dist=derivative_dtw_distance)
    dtw_costs_a.append(d)
    if d<min_cost_a:
        min_cost_a = d
        most_similar_win_a = ref_win
        prev_win = Da[i - len(missing_indices): i + len(missing_indices) - len(missing_indices)]
        print('New minima found')

plt.plot(Qa, color='blue')
plt.plot(most_similar_win_a, color='red')
plt.plot(prev_win, color='yellow') 

prev_win

plt.plot(prev_win, color='blue')
plt.plot(next_win, color='red')

x_c = x.copy()

df_17.isnull().sum()

plt.figure(figsize=(20,10))
plt.plot(df_17['W'][:288*10])

x[missing_indices]

x[missing_indices] = (prev_win+next_win)/2

x[missing_indices]

x[missing_indices].shape

plt.figure(figsize=(20,10))
plt.plot(df_17['W'][:288*5])

plt.figure(figsize=(20,10))
plt.plot(x[:288*5])















DTW_costs = []
for i in tqdm(range(0, len(Db)-len(missing_indices), step_threshold)):
    k = i + len(missing_indices) - 1
    Ri = Db[i:i+len(missing_indices)]
    d, cost_matrix, acc_cost_matrix, path = dtw(Qb, Ri, dist=derivative_dtw_distance)
    DTW_costs.append(d) 

a = np.array(DTW_costs)

threshold = np.nanmin(a)
threshold

i = np.where(a==threshold)[0][0]
Qbs = Db[i:i+len(missing_indices)]

Qbs

Db[i+len(missing_indices):len(missing_indices)]


