# Original model

## Sets

* $R$: Represents the relays in the system.
* $F$: Set of faults detected by each relay in each operating mode.
* $C$: Set of standard curves.


**Objective Function:**


$$\minimize \sum_{i \in R} \sum_{f \in F} t_{if}$$

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

#
