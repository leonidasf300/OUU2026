

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
\left[\left(\frac{A_c}{ \left(\frac{ICC_{if}}{Ipickup_{i}}\right)^{B_c} - 1 } \right) TMS_{ic} + x_{ic} C_c \right] \leq CTI 
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