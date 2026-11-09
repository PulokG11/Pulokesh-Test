# How to Play — Coffee Bean Optimization

Welcome to **Coffee Bean Optimization**, a classroom coffee-shop game about making decisions under uncertainty. You set brew rates, prices, and staffing; a live simulation shows how the shop responds; then you compare your plan to an expected-profit optimum.

**Play online:** [https://coffee-bean-optimization.netlify.app](https://coffee-bean-optimization.netlify.app)

Use a laptop or desktop for the best experience.

---

## Goal

Maximize **5-day (120-hour) profit** while keeping decisions **feasible** (enough beans and water).

Good play means balancing:

- brewing enough to serve demand
- not over-brewing (waste)
- pricing that keeps customers coming
- staffing that keeps the queue from walking away

Random arrivals mean the **same decisions can score differently each run**. The teaching target is **expected** performance, not one lucky day.

---

## Modes

### Play the Game

From the home page, choose **Play the Game**.

- Works through **8 progressive rounds**
- Optional anonymous play session (scores saved when a backend database is available)
- Best for learning, homework, and practice

### Championship Mode

From the home page, choose **Championship Mode**.

- **Students:** enter a match code + display name → **Join and play**
- **Instructors:** create a match with an API key, refresh the leaderboard, export CSV

Championship scores sum realized profits across the rounds you submit. Match codes are case-sensitive and up to 20 characters.

---

## Screen tour

| Area | What it does |
|------|----------------|
| **Round header** | Shows round number, title, and short description |
| **Round dots** | Jump between rounds 1–8 |
| **Coffee Shop Floor** | Live animation of queue, barista, and brew inventory |
| **Decisions panel** | Sliders for the active decision variables |
| **Feasible / Infeasible** | Green = allowed; red = breaks bean/water limits |
| **Constraint Monitor** | Beans and water used vs capacity |
| **Bean Guide tip** | Round-specific teaching hint |
| **Comparison screen** | Appears after Submit — you vs the optimizer |

---

## Core loop (every round)

1. **Read** the round description and Bean Guide tip.
2. **Move the sliders** to set a candidate plan.
3. Watch **Feasible / Infeasible**. If red, reduce brewing until constraints clear.
4. Click **Try Solution** to restart the live shop preview with your plan.
5. Let the simulation **warm up** — early empty-shop minutes look noisy; wait until the queue and profit settle.
6. When ready, click **Submit Solution**.
7. Study the **comparison screen**, then **Next round** or **Replay round**.

Nothing is graded until you **Submit**. Try Solution is for experimentation only.

---

## Decision variables

Depending on the round, you may control:

| Slider | Meaning |
|--------|---------|
| **Hot brew / hour** | Cups of hot coffee prepared each hour |
| **Cold brew / hour** | Cups of cold coffee prepared each hour |
| **Price markup** | Extra margin on drink prices (higher markup → fewer arrivals) |
| **Barista service rate** | Average customers the barista can serve per hour (higher rate → higher wage cost) |

### Feasibility

Brewing consumes **beans** and **water**. If usage exceeds capacity, the panel turns **Infeasible** and Submit is blocked. Feasible is necessary but not sufficient — many feasible plans still lose money.

---

## Watching the simulation

Customers arrive randomly (Poisson process) and join a queue.

- Thought bubbles: **♨** hot preference, **❄** cold preference
- If the line is long (later rounds), some customers **balk** and leave
- If inventory is empty, arrivals can leave as **stockout**
- Unused brew each hour becomes **waste**

**Warm-up vs steady state:** the shop starts empty. Early metrics swing. Let simulated time run before judging a plan — the same idea used in real operations research simulations.

Use the **Speed** control (1× / 2× / 4×) to advance faster while you experiment.

---

## Submitting and comparing

**Submit Solution** sends your slider values to the server, which:

1. Checks feasibility
2. Runs an authoritative **120-hour** seeded simulation (your realized 5-day profit)
3. Solves for decisions that maximize **expected** profit
4. Returns a comparison chart

### How to read the comparison chart

- **Curve** — expected profit as one decision variable changes
- **Filled markers** — expected profit for your plan and the optimizer
- **Hollow markers** — what happened on **this** random 5-day run

You can beat the optimizer on a single run by luck. That does not mean your plan is better in expectation. Ask: *which plan would I trust before knowing how randomness unfolds?*

---

## Round-by-round guide

### Round 1 — Steam Ahead

**Decisions:** hot brew only.

Learn the newsvendor trade-off: brew too little and you miss sales; brew too much and inventory sits unused. Start near expected demand, then nudge while watching live profit.

### Round 2 — Hot and Cold

**Decisions:** hot + cold brew.

Two products share bean and water limits. Balancing both drinks matters; maxing one can starve the other.

### Round 3 — Waste Costs Money

**New effect:** hot coffee has a brewing cost.

Leftovers now hurt the bottom line. The best brew quantity usually drops below “raw demand.”

### Round 4 — Both Drinks Cost

**New effect:** cold coffee is costly too.

Over-brewing either drink burns margin. Compare the two products separately when you experiment.

### Round 5 — Price Matters

**New decision:** markup.

Higher prices raise margin per cup but shrink arrivals. Profit becomes a hill: too cheap or too expensive both hurt. Look for the peak.

### Round 6 — The Line Walks Away

**New effect:** balking.

Crowded queues make customers leave. Congestion and waiting matter alongside brew quantities. Let the sim warm up before judging.

### Round 7 — Bigger Orders

**New effect:** multi-cup orders.

Some customers buy more than one cup, scaling effective demand. Randomness is louder; trust expected profit over one lucky score.

### Round 8 — Hire the Barista

**New decision:** service rate.

A faster barista clears the line but costs more wages. Balance lost sales from queues against labor cost — another nonlinear trade-off.

---

## Tips for a strong score

1. **Stay feasible** before optimizing performance.
2. **Try, then submit** — use Try Solution to build intuition; Submit for the scored result.
3. **Don’t chase one lucky day** — compare expected values on the chart.
4. **Change one slider at a time** when you are stuck.
5. **Watch waste and balking** in later rounds; raw “brew more” stops working.
6. In championships, **submit every round** — totals sum realized profits across rounds.

---

## Championship checklist (students)

1. Get the match code from your instructor.
2. Open [Championship Mode](https://coffee-bean-optimization.netlify.app/championship).
3. Enter the code and a display name → Join and play.
4. Complete rounds and Submit each one.
5. Confirm your name appears on the class leaderboard.

## Championship checklist (instructors)

1. Use the instructor API key configured on the backend (`INSTRUCTOR_API_KEY`).
2. Create a unique match code.
3. Share the code with the class.
4. Refresh the leaderboard or **Export CSV** when the session ends.

More classroom pacing notes: [INSTRUCTOR.md](INSTRUCTOR.md).

---

## What you should learn

By the end of eight rounds you should have felt that:

1. Feasibility is necessary, but not sufficient.
2. Randomness makes individual outcomes unpredictable.
3. Nonlinear systems do not respond smoothly to small changes.
4. Simulation is essential when systems evolve over time.
5. Optimization focuses on expected performance, not perfect prediction.

---

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| Sliders stuck / can’t Submit | Decision is **Infeasible** — lower brew rates |
| Profit looks crazy at the start | Wait for warm-up; early empty-shop metrics are unstable |
| Beat the optimizer once | Expected; compare filled markers, not one hollow marker |
| Championship join fails | Check match code spelling/case; ask instructor to create the match |
| Page won’t load locally | Start backend (`:8000`) and frontend (`:5173`); see [README](../README.md) |

---

## Links

- **Game:** [https://coffee-bean-optimization.netlify.app](https://coffee-bean-optimization.netlify.app)
- **API health:** [https://coffee-bean-api-two.vercel.app/health](https://coffee-bean-api-two.vercel.app/health)
- **Repository:** [https://github.com/PulokG11/Pulokesh-Test](https://github.com/PulokG11/Pulokesh-Test)
- **Instructor guide:** [INSTRUCTOR.md](INSTRUCTOR.md)
