# Determinism Test

This should test that the determinism checks are working ok.

* `determinism_equal.yaml` should pass
* `determinism_system_bigger` should drop the `c` when it hears it and pass
* `determinism_model_bigger` should check if the model is deterministic after hiding the `c`, which it is not, so it should abort
