import numpy as np
from sklearn.ensemble import BaggingClassifier
import kaggle_ninja

def random_query(X, y, model, batch_size, seed):
    X = X[np.invert(y.known)]
    np.random.seed(seed)
    ids = np.random.randint(0, X.shape[0], size=batch_size)
    return y.unknown_ids[ids]

def uncertainty_sampling(X, y, model, batch_size, seed=None):
    X = X[np.invert(y.known)]
    if hasattr(model, "decision_function"):
        # Settles page 12
        ids =  np.argsort(np.abs(model.decision_function(X)))[:batch_size]
    elif hasattr(model, "predict_proba"):
        assert hasattr(model, 'predict_proba'), "Model with probability prediction needs to be passed to this strategy!"
        p = model.predict_proba(X)
        # Settles page 13
        ids =  np.argsort(np.sum(p * np.log(p), axis=1))[:batch_size]
    return y.unknown_ids[ids]


# TODO: test with 2D uncertainty plot
def query_by_bagging(X, y, base_model, batch_size, seed, n_bags, method):
    assert method == 'entropy' or method == 'KL'
    if method == 'KL':
        assert hasattr(base_model, 'predict_proba'), "Model with probability prediction needs to be passed to this strategy!"
    clfs = BaggingClassifier(base_model, n_estimators=n_bags, random_state=seed)
    clfs.fit(X[y.known], y[y.known])
    pc = clfs.predict_proba(X[np.invert(y.known)])

    # Settles page 17
    if method == 'entropy':
        return np.argsort(np.sum(pc * np.log(pc), axis=1))[:batch_size]
    elif method == 'KL':
        p = np.array([clf.predict_proba(X[np.invert(y.known)]) for clf in clfs.estimators_])
        return np.argsort(np.mean(np.sum(p * np.log(p / pc), axis=2), axis=0))[-batch_size:]

kaggle_ninja.register("query_by_bagging", query_by_bagging)
kaggle_ninja.register("uncertanity_sampling", uncertainty_sampling)
kaggle_ninja.register("random_query", random_query)