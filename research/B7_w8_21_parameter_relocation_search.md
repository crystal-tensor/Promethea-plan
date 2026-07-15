# B7 w8_21 Parameter Relocation Search

- Status: `parameter_relocation_search_complete_no_five_angle_context_replay`
- Method: `b7_w8_21_parameter_relocation_search_v0`
- Contexts tested: `7`
- Relocated families tested per context: `243`
- Optimizer runs: `3402`
- Exact context replays: `0/7`
- Best residual norm: `0.03046391998887225`

## Question

Can five arbitrary Euler angles be relocated while retaining two CX gates and one pi scaffold, absorbing the seven external target-local Rz contexts without a sixth carrier?

## Scope

The search keeps two CX gates and the exact `mid:q1:rz1=pi` scaffold, then relocates five arbitrary Euler angles. It retains at least four of the five source arbitrary slots and excludes the exact source placement. Each family is tested against the seven source-bound external target-local Rz contexts selected by the neighborhood gate.

## Result

No exact five-angle relocated-family replay was found in the declared bounded search.

| Context | Direction | Best residual | Best family |
|---:|---|---:|---|
| 1 | after | 0.03046391998887225 | `cx01-cx01|fixed[mid:q1:rz1=pi]|free[pre:q1:ry,mid:q1:rz0,mid:q1:ry,post:q1:rz0,post:q1:ry]` |
| 2 | after | 0.03046391998887225 | `cx01-cx01|fixed[mid:q1:rz1=pi]|free[pre:q1:ry,mid:q1:rz0,mid:q1:ry,post:q1:rz0,post:q1:ry]` |
| 3 | after | 0.03046391998887225 | `cx01-cx01|fixed[mid:q1:rz1=pi]|free[pre:q1:ry,mid:q1:rz0,mid:q1:ry,post:q1:rz0,post:q1:ry]` |
| 4 | after | 0.03046391998887225 | `cx01-cx01|fixed[mid:q1:rz1=pi]|free[pre:q1:ry,mid:q1:rz0,mid:q1:ry,post:q1:rz0,post:q1:ry]` |
| 5 | after | 0.03046391998887225 | `cx01-cx01|fixed[mid:q1:rz1=pi]|free[pre:q1:ry,mid:q1:rz0,mid:q1:ry,post:q1:rz0,post:q1:ry]` |
| 6 | after | 0.03046391998887225 | `cx01-cx01|fixed[mid:q1:rz1=pi]|free[pre:q1:ry,mid:q1:rz0,mid:q1:ry,post:q1:rz0,post:q1:ry]` |
| 7 | after | 0.03046391998887225 | `cx01-cx01|fixed[mid:q1:rz1=pi]|free[pre:q1:ry,mid:q1:rz0,mid:q1:ry,post:q1:rz0,post:q1:ry]` |

## Claim Boundary

The result closes only the declared five-angle relocated Euler family over the seven selected contexts. It is not a global minimality theorem, not a proof that six parameters are necessary in every circuit, and not a full-circuit rewrite or B7 resource credit.

- Accepted occurrence removal: `0`
- Accepted proxy-T reduction: `0`
- B7 credit: `0`

## Next Route

The remaining high-value route is symbolic: characterize whether the external Rz changes a local invariant that cannot be represented by the retained five-angle two-CX family, then test a genuinely different Clifford scaffold or an occurrence-removing rewrite.
