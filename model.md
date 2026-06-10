# Robust model v2 (Corrected Relay Notation)

## New definitions

* $TMS_{ic} = y_{ic}$
* $\beta_{fic} = \frac{A_c}{ \left(\frac{ICC_{if}}{Ipickup_{i} \cdot CTR_i}\right)^{B_c} - 1 }$
* $f=1$
* $\tilde{\beta}_{j,c} = \beta^0_c + \beta^l_c \zeta \quad \text{where } \zeta \in [-1,1] \text{ and } j \text{ is the backup relay}$

## Sets

* $R$: Set of relays in the system $R = \{R1, R2, R3\}$.
* $F$: Set of faults detected by each relay in each operating mode.
* $C$: Set of standard curves.
* $P$: Set of coordination pairs $P = \{(R2, R1), (R3, R1), (R3, R2)\}$ where each element is a tuple $(i, j)$ representing (Principal, Backup).

## Parameters

* $A_c, B_c, C_c$: Standard curve parameters for curve $c \in C$.
* $y_{ub}, y_{lb}$: TMS upper and lower bounds for the TMS.
* $ICC_{if}$: Short-circuit current seen by relay $i$ during fault $f$.
* $Ipickup_i$: Pickup current for relay $i \in R$.
* $CTR_i$: CT ratio for relay $i \in R$.
* $CTI$: Coordination time interval.
* $k1_{c,q}, k2_{c,q}$: Linear coupling parameters for the curve pair $(c,q) \in C^2$.
* $\beta^0_q$: Nominal value of the curve parameter for the backup relay under curve $q \in C$.
* $\beta^l_q$: Uncertainty budget/half-length limit for the backup relay under curve $q \in C$.
* $M$: A large positive constant (Big-M).

## Decision variables

* $y_{ic}$: Time Multiplier Setting (TMS) for relay $i \in R$ and curve $c \in C$.
* $x_{ic}$: Auxiliary Binary variable for curve selection for relay $i \in R$ and curve $c \in C$.
* $z_{i,j,q,c}$: Auxiliary continuous variable to linearize the robust protection term for the relay pair $(i,j) \in P$ and curve pair $(q,c) \in C^2$.

**Objective Function:**

$$\text{minimize} \sum_{c \in C} \sum_{i \in R} \sum_{f \in F}  \beta_{fic} y_{ic} + x_{ic} C_c $$

**Subject to:**

* **Curve selection (only one curve per relay):**

$$\sum_{c \in C} x_{ic} = 1 \quad \forall i \in R$$

* **Time multiplier setting (TMS) bounds:**

$$y_{ic} \leq y_{ub} x_{ic} \quad \forall i \in R, c \in C$$

$$y_{ic} \geq y_{lb} x_{ic} \quad \forall i \in R, c \in C$$

* **Robust Coordination Constraints for All Pairs (P):**

For each coordination pair $(i,j) \in P$ where relay $i$ is the principal and relay $j$ is the backup, the coordination must hold for any combination of curves $(q,c) \in C^2$ under the worst-case scenario of uncertainty.

$$\left( k1_{c,q} y_{i,c} + k2_{c,q} \beta^0_q y_{i,c} - \beta^0_q y_{j,q} - C_c - C_q + CTI \right) + z_{i,j,q,c} \leq M(2 - x_{j,q} - x_{i,c}) \quad \forall (i,j) \in P, \forall q,c \in C^2$$

$$z_{i,j,q,c} \geq \left( k2_{c,q} \beta^l_q y_{i,c} - \beta^l_q y_{j,q} \right) - M(2 - x_{j,q} - x_{i,c}) \quad \forall (i,j) \in P, \forall q,c \in C^2$$

$$z_{i,j,q,c} \geq -\left( k2_{c,q} \beta^l_q y_{i,c} - \beta^l_q y_{j,q} \right) - M(2 - x_{j,q} - x_{i,c}) \quad \forall (i,j) \in P, \forall q,c \in C^2$$

* **Explicit Expansion of the Robust Constraints for your system:**

### 1. Pair (R2, R1) -> R2 is Principal (i), R1 is Backup (j)
$$\left( k1_{c,q} y_{R2,c} + k2_{c,q} \beta^0_q y_{R2,c} - \beta^0_q y_{R1,q} - C_c - C_q + CTI \right) + z_{R2,R1,q,c} \leq M(2 - x_{R1,q} - x_{R2,c}) \quad \forall q,c \in C^2$$
$$z_{R2,R1,q,c} \geq \left( k2_{c,q} \beta^l_q y_{R2,c} - \beta^l_q y_{R1,q} \right) - M(2 - x_{R1,q} - x_{R2,c}) \quad \forall q,c \in C^2$$
$$z_{R2,R1,q,c} \geq -\left( k2_{c,q} \beta^l_q y_{R2,c} - \beta^l_q y_{R1,q} \right) - M(2 - x_{R1,q} - x_{R2,c}) \quad \forall q,c \in C^2$$

### 2. Pair (R3, R1) -> R3 is Principal (i), R1 is Backup (j)
$$\left( k1_{c,q} y_{R3,c} + k2_{c,q} \beta^0_q y_{R3,c} - \beta^0_q y_{R1,q} - C_c - C_q + CTI \right) + z_{R3,R1,q,c} \leq M(2 - x_{R1,q} - x_{R3,c}) \quad \forall q,c \in C^2$$
$$z_{R3,R1,q,c} \geq \left( k2_{c,q} \beta^l_q y_{R3,c} - \beta^l_q y_{R1,q} \right) - M(2 - x_{R1,q} - x_{R3,c}) \quad \forall q,c \in C^2$$
$$z_{R3,R1,q,c} \geq -\left( k2_{c,q} \beta^l_q y_{R3,c} - \beta^l_q y_{R1,q} \right) - M(2 - x_{R1,q} - x_{R3,c}) \quad \forall q,c \in C^2$$

### 3. Pair (R3, R2) -> R3 is Principal (i), R2 is Backup (j)
$$\left( k1_{c,q} y_{R3,c} + k2_{c,q} \beta^0_q y_{R3,c} - \beta^0_q y_{R2,q} - C_c - C_q + CTI \right) + z_{R3,R2,q,c} \leq M(2 - x_{R2,q} - x_{R3,c}) \quad \forall q,c \in C^2$$
$$z_{R3,R2,q,c} \geq \left( k2_{c,q} \beta^l_q y_{R3,c} - \beta^l_q y_{R2,q} \right) - M(2 - x_{R2,q} - x_{R3,c}) \quad \forall q,c \in C^2$$
$$z_{R3,R2,q,c} \geq -\left( k2_{c,q} \beta^l_q y_{R3,c} - \beta^l_q y_{R2,q} \right) - M(2 - x_{R2,q} - x_{R3,c}) \quad \forall q,c \in C^2$$

* **Variable domains:**

$$y_{ic} \geq 0 \quad \forall i \in R, c \in C$$
$$x_{ic} \in \{0,1\} \quad \forall i \in R, c \in C$$
$$z_{i,j,q,c} \geq 0 \quad \forall (i,j) \in P, \forall q,c \in C^2$$

# Deterministic model v2 (Nominal Parameters Only)

## Definitions

* $TMS_{ic} = y_{ic}$
* $\beta_{fic} = \frac{A_c}{ \left(\frac{ICC_{if}}{Ipickup_{i} \cdot CTR_i}\right)^{B_c} - 1 }$
* $f=1$
* $c=1$
* $\beta_{j,q} = \beta^0_q \quad \text{where } \beta^0_q \text{ is the nominal deterministic parameter for the backup relay}$

## Sets

* $R$: Set of relays in the system $R = \{R1, R2, R3\}$.
* $F$: Set of faults detected by each relay in each operating mode.
* $C$: Set of standard curves.
* $P$: Set of coordination pairs $P = \{(R2, R1), (R3, R1), (R3, R2)\}$ where each element is a tuple $(i, j)$ representing (Principal, Backup).

## Parameters

* $A_c, B_c, C_c$: Standard curve parameters for curve $c \in C$.
* $y_{ub}, y_{lb}$: TMS upper and lower bounds for the TMS.
* $ICC_{if}$: Short-circuit current seen by relay $i$ during fault $f$.
* $Ipickup_i$: Pickup current for relay $i \in R$.
* $CTR_i$: CT ratio for relay $i \in R$.
* $CTI$: Coordination time interval.
* $k1_{c,q}, k2_{c,q}$: Linear coupling parameters for the curve pair $(c,q) \in C^2$.
* $\beta^0_q$: Nominal value of the curve parameter for the backup relay under curve $q \in C$.
* $M$: A large positive constant (Big-M).

## Decision variables

* $y_{ic}$: Time Multiplier Setting (TMS) for relay $i \in R$ and curve $c \in C$.
* $x_{ic}$: Auxiliary Binary variable for curve selection for relay $i \in R$ and curve $c \in C$.

**Objective Function:**

$$\text{minimize} \sum_{c \in C} \sum_{i \in R} \sum_{f \in F}  \beta_{fic} y_{ic} + x_{ic} C_c $$

**Subject to:**

* **Curve selection (only one curve per relay):**

$$\sum_{c \in C} x_{ic} = 1 \quad \forall i \in R$$

* **Time multiplier setting (TMS) bounds:**

$$y_{ic} \leq y_{ub} x_{ic} \quad \forall i \in R, c \in C$$

$$y_{ic} \geq y_{lb} x_{ic} \quad \forall i \in R, c \in C$$

* **Deterministic Coordination Constraints for All Pairs (P):**

For each coordination pair $(i,j) \in P$ where relay $i$ is the principal and relay $j$ is the backup, the coordination must hold for any combination of curves $(q,c) \in C^2$ using strictly the nominal parameter $\beta^0_q$.

$$\left( k1_{c,q} y_{i,c} + k2_{c,q} \beta^0_q y_{i,c} - \beta^0_q y_{j,q} - C_c - C_q + CTI \right) \leq M(2 - x_{j,q} - x_{i,c}) \quad \forall (i,j) \in P, \forall q,c \in C^2$$

* **Explicit Expansion of the Deterministic Constraints for your system:**

### 1. Pair (R2, R1) -> R2 is Principal (i), R1 is Backup (j)
$$\left( k1_{c,q} y_{R2,c} + k2_{c,q} \beta^0_q y_{R2,c} - \beta^0_q y_{R1,q} - C_c - C_q + CTI \right) \leq M(2 - x_{R1,q} - x_{R2,c}) \quad \forall q,c \in C^2$$

### 2. Pair (R3, R1) -> R3 is Principal (i), R1 is Backup (j)
$$\left( k1_{c,q} y_{R3,c} + k2_{c,q} \beta^0_q y_{R3,c} - \beta^0_q y_{R1,q} - C_c - C_q + CTI \right) \leq M(2 - x_{R1,q} - x_{R3,c}) \quad \forall q,c \in C^2$$

### 3. Pair (R3, R2) -> R3 is Principal (i), R2 is Backup (j)
$$\left( k1_{c,q} y_{R3,c} + k2_{c,q} \beta^0_q y_{R3,c} - \beta^0_q y_{R2,q} - C_c - C_q + CTI \right) \leq M(2 - x_{R2,q} - x_{R3,c}) \quad \forall q,c \in C^2$$

* **Variable domains:**

$$y_{ic} \geq 0 \quad \forall i \in R, c \in C$$
$$x_{ic} \in \{0,1\} \quad \forall i \in R, c \in C$$
