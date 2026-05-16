# Pro Machina
A production scheduling toolkit for optimising complex manufacturing processes.

## Introduction
A number of highly complex problems arise in the planning of production across multiple machines within a production facility. This problem, although it is NP-Hard, is heavily studied and often referred to as the [Job-shop scheduling problem](https://en.wikipedia.org/wiki/Job-shop_scheduling) or, more broadly, [Optimal job scheduling](https://en.wikipedia.org/wiki/Optimal_job_scheduling). These problems are often approached using some form of linear programming to maximise a cost function and, indeed, there are many articles and libraries to support manufacturers in this area.

However, all of these approaches assume that production runs are for fixed periods of time. That is, if you have three tasks (A, B and C), you know how long each of those tasks take, and you have to ensure that A is completed before B, and B before C etc. That is not how things work in _many_ manufacturing environments, particularly in relation to Fast-Moving Consumer Goods (FMCG) / Consumer Packaged Goods (CPG).

That is the domain of Pro Machina.

## Scenario
You are trying to optimise production across a sweet factory (this is based on a real example where this model was first developed):
- 88 machines across 7 departments
- 650 WIP items (individual type of sweet) can be produced across those machines
- Machines have complex shift patterns
- 200 Finished Products (that is, unique mixtures of sweets from multiple departments in varying proportions) have an aggregated sales forecast
- Storage of stock is limited. Overproduction of one item will consume storage space. However, only having 9 WIP components out of 10 required to meet the product specification means that the finished product cannot be made *at all*
- Major supermarkets can impose severe fines for missed OTIF targets
- Upstream of making the individual sweets, batches of the hot sugar syrup need to be made and used within a set time period but can be allocated to multiple different WIP items, across multiple machines
- Production runs of any one sweet can be entirely variable. You could run the machine making one WIP item for anywhere between two hours and 24 hours. The machines also run at different speeds depending on the WIP they are producing
- Machines run slower during the summer months because the high humidity causes the batch rollers to slip on the hardening sugar
- Some machines can be reconfigured at short notice (i.e. change a die in the press) to swap to producing an entirely different subset of WIP items
- Halloween is a massive rush period, so products for these promotional items _will_ need to be stockpiled
- Gelatin-free variants of WIP items require a machine shutdown for deep cleaning, so product categories should be grouped together where practical

... and the list goes on. Particularly with the variable-length production runs, this kind of problemn is unsuitable to traditional approaches to optimisation. Pro Machina takes a custom heuristic approach to solving this problem.

## Status
Although such a model has been built and used in production for over 6 years now for the above scenario, an attempt is being made here to generalise the kind of constraints to be applicable across the FMCG industry. Right now, the package itself is very much WIP itself, focused on getting the fundamentals right to support such a broad range of constraints.

## Installation and Use
```python
pip install pro_machina
```
The vast majority of the interface is fully documented in the library itself but the constraint interface is currently under development. The best way to see how the library works is to look in the [examples folder](https://github.com/Pro-Machina-Solutions/pro_machina/tree/main/examples) (examples 01-04 for now) to see the direction of travel.


