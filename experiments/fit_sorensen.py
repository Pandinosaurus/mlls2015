from experiment_runner import run_experiment
from experiments import fit_grid
import numpy as np
import sys
from get_data import proteins

def run(protein, fingerprint="PubchemFP"):

    seed = 666
    warm_start_percentage = 0.05
    param_grid = {'C': list(np.logspace(-3, 4, 8))}

    loader = ["get_splitted_data_clusterwise", {
        "seed": seed,
        "valid_size": 0.1,
        "n_folds": 5}]


    preprocess_fncs = [["to_binary", {"all_below": True}]]

    for batch_size in [20, 50, 100]:

        for c in list(np.linspace(0.1, 0.9, 9)):
            svmtan_exp = run_experiment("fit_grid",
                                    force_reload=False,
                                    recalculate_experiments=False,
                                    n_jobs=5,
                                    experiment_detailed_name="fit_SVMTAN_czarnecki_two_clusters_sorensen_c_%.2f_%s_%s_%s" % (c, protein, fingerprint, str(batch_size)),
                                    base_experiment="fit_active_learning",
                                    seed=seed,
                                    grid_params={"strategy_kwargs:c": [c],
                                                 "strategy_kwargs:projection": ['sorensen']},
                                    base_experiment_kwargs={"strategy": "czarnecki_two_clusters",
                                                            "preprocess_fncs": preprocess_fncs,
                                                            "protein": protein,
                                                            "fingerprint": fingerprint,
                                                            "warm_start_percentage": warm_start_percentage,
                                                            "batch_size": batch_size,
                                                            "base_model": "SVMTAN",
                                                            "loader_function": loader[0],
                                                            "loader_args": loader[1],
                                                            "param_grid": param_grid})

if __name__ == '__main__':

    assert len(sys.argv) >= 1, "pass one protein and batch_size"
    protein = sys.argv[1]
    assert protein in proteins, "please pick one of proteins: %s" % proteins

    run(protein, "ExtFP")
    run(protein, "PubchemFP")
    run(protein, "MACCSFP")