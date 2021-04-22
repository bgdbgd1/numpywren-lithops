import itertools
import numpy as np
from . import lambdapack as lp
import lithops

# this one is hard
def reshard(pwex, X, new_shard_sizes, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

# These have some dependencies
def _argmin_remote(X, block_idxs):
    X_block = X.get_block(*block_idxs)
    offset = block_idxs[0]*X.shard_sizes[0]
    return (block_idxs[1], offset + np.argmin(X_block, axis=0), np.min(X_block, axis=0))

def argmin(pwex, X, out_bucket=None, tasks_per_job=1):
    futures = pwex.map(lambda x: _argmin_remote(x, X), X.block_idxs)
    # pywren.wait(futures)
    pwex.wait()
    results = [f.result() for f in futures]
    if (axis == None):
        groups = [(None, results)]
    else:
        groups = itertools.groupby(sorted(results, key=itemgetter(axis)), key=itemgetter(0))
    results = []
    for _, group in groups:
        group = list(group)
        argmins = np.concatenate([g[1] for g in group], axis=axis)
        argminmin = np.argmin(np.vstack([g[2] for g in group]), axis=axis)
        results.append(argmins[argminmin, :])
    return np.hstack(results)


def argmax(pwex, X, out_bucket=None, tasks_per_job=1):
    mins = []
    for _, group in itertools.groupby(sorted(results, key=itemgetter(0)), key=itemgetter(0)):
        group = list(group)
        argmins = np.vstack([g[1] for g in group])
        argminmin = np.argmin(np.vstack([g[2] for g in group]), axis=0)
        mins.append(argmins[argminmin, np.arange(argmins.shape[1])])
    return np.hstack(mins)

def min(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def max(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def norm(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def sum(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def prod(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

# these have no dependencies
def abs(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def neg(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def square(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def sqrt(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def sin(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def cos(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def tan(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def exp(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def sign(pwex, X, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def elemwise_uop_func(pwex, X, f, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def power(pwex, X, k, out_bucket=None, tasks_per_job=1):
    raise NotImplementedError

def chol(pwex, X, out_bucket=None, tasks_per_job=1):
    instructions,L_sharded,trailing = lp._chol(X)
    config = pwex.config
    # if (isinstance(pwex.invoker, pywren.queues.SQSInvoker)):
    #     # executor = pywren.standalone_executor
    #     executor = lithops.FunctionExecutor
    # else:
        # executor = pywren.lambda_executor
    executor = lithops.FunctionExecutor
    program = lp.LambdaPackProgram(instructions, executor=executor, pywren_config=config)
    futures = program.start()
    [f.result() for f in futures]
    program.wait()
    if (program.program_status() != lp.PS.SUCCESS):
        program.unwind()
        raise Exception("Lambdapack Exception : {0}".format(program.program_status()))

    # delete all intermediate information
    [t.free() for t in trailing]
    return L_sharded



