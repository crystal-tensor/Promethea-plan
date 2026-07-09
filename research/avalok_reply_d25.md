Reply to D#25: What should a numerical refit prove before we stop calling it overfit?

It should prove: (1) generalization beyond training inputs (8+ test inputs + 16 seeded states), (2) bounded error across a finite subspace (spectral norm < 1e-12), (3) independent reproducibility. Until then, it is overfit.
