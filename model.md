# Robust model v2 (Corrected Relay Notation)

## New definitions

* $TMS_{ic} = y_{ic}$
* $\beta_{fic} = \frac{A_c}{ \left(\frac{ICC_{if}}{Ipickup_{i} \cdot CTR_i}\right)^{B_c} - 1 }$
* $f=1$
* $c=1$
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

# Robust model v2 (Uncertainty Integrated)

## New definitions

* $TMS_{ic} = y_{ic}$
* $\beta_{fic} = \frac{A_c}{ \left(\frac{ICC_{if}}{Ipickup_{i} \cdot CTR_i}\right)^{B_c} - 1 }$
* $f=1$
* $c=1$
* $\tilde{\beta}_{1,c} = \beta^0_c + \beta^l_c \zeta \quad \text{where } \zeta \in [-1,1]$

## Sets

* $R$: Set of relays in the system.
* $F$: Set of faults detected by each relay in each operating mode.
* $C$: Set of standard curves.

## Parameters

* $A_c, B_c, C_c$: Standard curve parameters for curve $c \in C$.
* $y_{ub}, y_{lb}$: TMS upper and lower bounds for the TMS.
* $ICC_{if}$: Short-circuit current seen by relay $i$ during fault $f$.
* $Ipickup_i$: Pickup current for relay $i \in R$.
* $CTR_i$: CT ratio for relay $i \in R$.
* $CTI$: Coordination time interval.
* $k1_{c,q}, k2_{c,q}$: Linear coupling parameters for the curve pair $(c,q) \in C^2$.
* $\beta^0_c$: Nominal value of the curve parameter for the backup relay under curve $c \in C$.
* $\beta^l_c$: Uncertainty budget/half-length limit for the backup relay under curve $c \in C$.
* $M$: A large positive constant (Big-M).
* Backup relay matrix:

$$BU_{ij} = 
\begin{cases} 
1, & \text{relay } j \text{ is the backup of relay } i \quad \forall i,j \in R \\ 
0, & \text{relay } j \text{ is NOT the backup of relay } i \quad \forall i,j \in R 
\end{cases}$$

## Decision variables

* $y_{ic}$: Time Multiplier Setting (TMS) for relay $i$ and curve $c$.
* $x_{ic}$: Auxiliary Binary variable for curve selection.
* $z_{q,c}$: Auxiliary continuous variable to linearize the robust protection term ($\forall q,c \in C^2, z_{q,c} \geq 0$).

**Objective Function:**

$$\text{minimize} \sum_{c \in C} \sum_{i \in R} \sum_{f \in F}  \beta_{fic} y_{ic} + x_{ic} C_c $$

**Subject to:**

* **General Coordination time interval (Nominal Pairs):**

$$\sum_{c \in C} \left[ \beta_{fjc} y_{jc} + x_{jc} C_c - \beta_{fic} y_{ic} - x_{ic} C_c \right] \geq CTI \quad \forall i,j \in R: i \neq j, f \in F, BU_{ij} = 1$$

* **Robust Coordination Constraints (For Relay 1 = Backup, Relay 2 = Principal):**

Para el par donde existe incertidumbre, al sustituir $\tilde{\beta}_{1,q} = \beta^0_q + \beta^l_q \zeta$ y evaluar el peor caso de $\zeta \in [-1,1]$ que maximiza el lado izquierdo de la inecuación $\leq 0$, el modelo se protege mediante las siguientes restricciones lineales acopladas por Big-M para cada combinación de curvas $(q,c) \in C^2$:

$$\left( k1_{c,q} y_{2,c} + k2_{c,q} \beta^0_q y_{2,c} - \beta^0_q y_{1,q} + C_c - C_q + CTI \right) + z_{q,c} \leq M(2 - x_{1,q} - x_{2,c}) \quad \forall q,c \in C^2$$

$$z_{q,c} \geq \left( k2_{c,q} \beta^l_q y_{2,c} - \beta^l_q y_{1,q} \right) - M(2 - x_{1,q} - x_{2,c}) \quad \forall q,c \in C^2$$

$$z_{q,c} \geq -\left( k2_{c,q} \beta^l_q y_{2,c} - \beta^l_q y_{1,q} \right) - M(2 - x_{1,q} - x_{2,c}) \quad \forall q,c \in C^2$$

* **Curve selection (only one curve per relay):**

$$\sum_{c \in C} x_{ic} = 1 \quad \forall i \in R$$

* **Time multiplier setting (TMS) bounds:**

$$y_{ic} \leq y_{ub} x_{ic} \quad \forall i \in R, c \in C$$

$$y_{ic} \geq y_{lb} x_{ic} \quad \forall i \in R, c \in C$$

* **Variable domains:**

$$y_{ic} \geq 0 \quad \forall i \in R, c \in C$$

$$x_{ic} \in \{0,1\} \quad \forall i \in R, c \in C$$

$$z_{q,c} \geq 0 \quad \forall q,c \in C^2$$


# Robust model v1

## New definitions

* $TMS_{ic} = y_{ic}$
* $\beta_{fic} = \frac{A_c}{ \left(\frac{ICC_{if}}{Ipickup_{i} \cdot CTR_i}\right)^{B_c} - 1 }$
* $f=1$
* $c=1$

## Sets

* $R$: Set of relays in the system.
* $F$: Set of faults detected by each relay in each operating mode.
* $C$: Set of standard curves.

## Parameters

* $A_c, B_c, C_c$: Standard curve parameters for curve $c \in C$.
* $y_{ub}, y_{lb}$: TMS upper and lower bounds for the TMS.
* $ICC_{if}$: Short-circuit current seen by relay $i$ during fault $f$.
* $Ipickup_i$: Pickup current for relay $i \in R$.
* $CTR_i$: CT ratio for relay $i \in R$.
* $CTI$: Coordination time interval.
* $k1_{c,q}, k2_{c,q}$: Linear coupling parameters for the curve pair $(c,q) \in C^2$.
* $\beta^0, \beta^l, \zeta$: Parameters for the backup relay's curve characterization.
* $M$: A large positive constant (Big-M).
* Backup relay matrix:

$$BU_{ij} = 
\begin{cases} 
1, & \text{relay } j \text{ is the backup of relay } i \quad \forall i,j \in R \\ 
0, & \text{relay } j \text{ is NOT the backup of relay } i \quad \forall i,j \in R 
\end{cases}$$

## Decision variables

* $y_{ic}$: Time Multiplier Setting (TMS) for relay $i$ and curve $c$.
* $x_{ic}$: Auxiliary Binary variable for curve selection.
* $\Omega_{2,c}$: Auxiliary continuous variable for the principal relay curve coupling ($\Omega_{2,c} \geq 0$).

**Objective Function:**

$$\text{minimize} \sum_{c \in C} \sum_{i \in R} \sum_{f \in F}  \beta_{fic} y_{ic} + x_{ic} C_c $$

**Subject to:**

* **Coordination time interval (CTI):**

$$\sum_{c \in C} \left[ \beta_{fjc} y_{jc} + x_{jc} C_c - \beta_{fic} y_{ic} - x_{ic} C_c \right] \geq CTI \quad \forall i,j \in R: i \neq j, f \in F, BU_{ij} = 1$$

For a specific coordination pair where **relay 1 is the backup** and **relay 2 is the principal**, the time margin requirement is expressed as:

$$\sum_{c \in C} \left[ \tilde{\beta_{1,c}} y_{1,c} + x_{1,c} C_c - \tilde{\beta_{2,c}} y_{2,c} - x_{2,c} C_c \right] - CTI \geq 0$$

The curve parameters are coupled such that the principal relay curve ($c$) depends on the backup relay curve ($q$):

$$\tilde{\beta_{2,c}} = k1_{c,q} + k2_{c,q} \tilde{\beta_{1,q}} \quad \forall c,q \in C$$

Notice that $c$ and $q$ are indices of the set $C$. Hence, all possible pairs of curves are considered, resulting in a combinatorial space of size $|C|^2$. To linearize this relationship without multiplying decision variables, we introduce the auxiliary variable $\Omega_{2,c} = \tilde{\beta_{2,c}} y_{2,c}$ via Big-M constraints:

$$\Omega_{2,c} \geq \left[ k1_{c,q} + k2_{c,q}\tilde{\beta_{1,q}} \right] y_{2,c} - M(2 - x_{1,q} - x_{2,c}) \quad \forall q,c \in C^2$$

$$\Omega_{2,c} \leq \left[ k1_{c,q} + k2_{c,q}\tilde{\beta_{1,q}} \right] y_{2,c} + M(2 - x_{1,q} - x_{2,c}) \quad \forall q,c \in C^2$$

Standardizing to the standard optimization format $\leq 0$:

$$\sum_{c \in C} \left[ \Omega_{2,c} + x_{2,c} C_c - \tilde{\beta_{1,c}} y_{1,c} - x_{1,c} C_c \right] + CTI \leq 0$$

Where the backup curve parameter is defined by:

$$\tilde{\beta_{1,c}} = \beta^0 + \beta^l \zeta$$

* **Curve selection (only one curve per relay):**

$$\sum_{c \in C} x_{ic} = 1 \quad \forall i \in R$$

* **Time multiplier setting (TMS) bounds:**

$$y_{ic} \leq y_{ub} x_{ic} \quad \forall i \in R, c \in C$$

$$y_{ic} \geq y_{lb} x_{ic} \quad \forall i \in R, c \in C$$

* **Variable domains:**

$$y_{ic} \geq 0 \quad \forall i \in R, c \in C$$

$$x_{ic} \in \{0,1\} \quad \forall i \in R, c \in C$$

$$\Omega_{2,c} \geq 0 \quad \forall c \in C$$

# Rewriting deterministic model v2

## New definitions

* $TMS_{ic} = y_{ic}$
* $\beta_{fic} = \frac{A_c}{ \left(\frac{ICC_{if}}{Ipickup_{i}*CTR_i}\right)^{B_c} - 1 }$
* $f=1$

## Sets

* $R$: Set of relays in the system.
* $F$: Set of faults detected by each relay in each operating mode.
* $C$: Set of standard curves.

## Parameters

* $A_c$, $B_c$, $C_c$ Standard curve parameters for curve $c \in C$.
* $y_{ub}$, $y_{lb}$: TMS upper and lower bounds for the TMS.
* $ICC_{if}$: Short-circuit current seen by relay i during fault f.
* $Ipickup_i$: Pickup current for relay $i \in R$
* $CTR_i$: CT ratio for relay $i \in R$.
* $CTI$: Coordination time interval.
* Backup relay matrix:

$$BU_{ij} = 
\begin{cases} 
1, & \text{relay } j \text{ is the backup of relay } i \quad \forall i,j \in R \\ 
0, & \text{relay } j \text{ is NOT the backup of relay } i \quad \forall i,j \in R 
\end{cases}$$

## Decision variables

* $y_{ic}$: Time Multiplier Setting 
* $x_{ic}$: Auxiliary Binary variable





**Objective Function:**



$$minimize \sum_{c \in C} \sum_{i \in R} \sum_{f \in F}  \beta_{ic} y_{ic} + x_{ic} C_c $$

**Subject to:**

* **Coordination time interval (CTI):**

$$
\sum_{c \in C} 
\left[ \beta_{jc} y_{jc} + x_{jc} C_c -
 \beta_{ic} y_{ic} - x_{ic} C_c \right] \geq CTI 
\quad \forall i,j \in R: i \neq j, f \in F, \beta_{fic} \geq 0, \beta_{fjc} \geq 0, BU_{ij} = 1$$


* **Curve selection (only one curve per relay):**

$\sum_{c \in C} x_{ic} = 1 \quad \forall i \in R$

* **Time multiplier setting (TMS) bounds:**

$y_{ic} \leq y_{ub} x_{ic} \quad \forall i \in R, c \in C$

$y_{ic} \geq y_{lb} x_{ic} \quad \forall i \in R, c \in C$

* **Variable domains:**
<!-- t_{if} \geq 0 \quad \forall i \in R, f \in F$  -->

$y_{ic} \geq 0 \quad \forall i \in R, c \in C$

$x_{ic} \in \{0,1\} \quad \forall i \in R, c \in C$

# Rewriting deterministic model


## Sets

* $R$: Set of relays in the system.
* $F$: Set of faults detected by each relay in each operating mode.
* $C$: Set of standard curves.

## Parameters

* $A_c$, $B_c$, $C_c$ Standard curve parameters for curve $c \in C$.
* $TMS_{ub}$, $TMS_{lb}$: TMS upper and lower bounds for the TMS.
* $ICC_{if}$: Short-circuit current seen by relay i during fault f.
* $Ipickup_i$: Pickup current for relay $i \in R$
* $CTI$: Coordination time interval.
* Backup relay matrix:

$$BU_{ij} = 
\begin{cases} 
1, & \text{relay } j \text{ is the backup of relay } i \quad \forall i,j \in R \\ 
0, & \text{relay } j \text{ is NOT the backup of relay } i \quad \forall i,j \in R 
\end{cases}$$

## Decision variables

* $TMS_{ic}$: Time Multiplier Setting 
* $x_{ic}$: Auxiliary Binary variable





**Objective Function:**


$$minimize \sum_{c \in C} \sum_{i \in R} \sum_{f \in F} \frac{A_c}{ \left(\frac{ICC_{if}}{Ipickup_{i}}\right)^{B_c} - 1 }  TMS_{ic} + x_{ic} C_c $$

**Subject to:**

* **Coordination time interval (CTI):**

$$
\sum_{c \in C} 
\left[\left(\frac{A_c}{ \left(\frac{ICC_{jf}}{Ipickup_{j}}\right)^{B_c} - 1 } \right) TMS_{jc} + x_{jc} C_c \right]-
\left[\left(\frac{A_c}{ \left(\frac{ICC_{if}}{Ipickup_{i}}\right)^{B_c} - 1 } \right) TMS_{ic} + x_{ic} C_c \right] \geq CTI 
\quad \forall i,j \in R: i \neq j, f \in F, \beta_{fic} \geq 0, \beta_{fjc} \geq 0, BU_{ij} = 1$$


* **Curve selection (only one curve per relay):**

$\sum_{c \in C} x_{ic} = 1 \quad \forall i \in R$

* **Time multiplier setting (TMS) bounds:**

$TMS_{ic} \leq TMS_{ub} x_{ic} \quad \forall i \in R, c \in C$

$TMS_{ic} \geq TMS_{lb} x_{ic} \quad \forall i \in R, c \in C$

* **Variable domains:**
<!-- t_{if} \geq 0 \quad \forall i \in R, f \in F$  -->

$TMS_{ic} \geq 0 \quad \forall i \in R, c \in C$

$x_{ic} \in \{0,1\} \quad \forall i \in R, c \in C$


# Original model

## Sets

* $R$: Represents the relays in the system.
* $F$: Set of faults detected by each relay in each operating mode.
* $C$: Set of standard curves.

$$
    PSM_{if} = \frac{ICC_{if}}{Ipickup_{i}} \quad \forall \quad i \in R, \quad f \in F
$$

$$
    \beta_{fic} = \frac{A_c}{ PSM_{if}^{B_c} - 1 } \quad \forall \quad i \in R, \quad f \in F, \quad c \in C
$$

**Backup relay matrix:**

$$BU_{ij} = 
\begin{cases} 
1, & \text{relay } j \text{ is the backup of relay } i \quad \forall i,j \in R \\ 
0, & \text{relay } j \text{ is NOT the backup of relay } i \quad \forall i,j \in R 
\end{cases}$$

**Objective Function:**


$$minimize \sum_{i \in R} \sum_{f \in F} t_{if}$$

**Subject to:**

* **Operation time calculation:**
$t_{if} = \sum_{c \in C} (\beta_{fic} TMS_{ic} + x_{ic} C_c) \quad \forall i \in R, f \in F, \beta_{fic} \geq 0$
* **Coordination time interval (CTI):**
$\sum_{c \in C} (\beta_{fjc} TMS_{jc} + x_{jc} C_c) - t_{if} \geq CTI \quad \forall i,j \in R: i \neq j, f \in F, \beta_{fic} \geq 0, \beta_{fjc} \geq 0, BU_{ij} = 1$
* **Curve selection (only one curve per relay):**
$\sum_{c \in C} x_{ic} = 1 \quad \forall i \in R$
* **Time multiplier setting (TMS) bounds:**
$TMS_{ic} \leq TMS_{ub} x_{ic} \quad \forall i \in R, c \in C$
$TMS_{ic} \geq TMS_{lb} x_{ic} \quad \forall i \in R, c \in C$
* **Variable domains:**
$t_{if} \geq 0 \quad \forall i \in R, f \in F$
$TMS_{ic} \geq 0 \quad \forall i \in R, c \in C$
$x_{ic} \in \{0,1\} \quad \forall i \in R, c \in C$
